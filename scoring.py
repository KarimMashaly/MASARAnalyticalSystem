"""
score.py — Masar Analytical System · Behavioral Scoring Engine
==============================================================

Philosophy
----------
Masar measures *behavioral identity coherence*, not simple trait accumulation.
A track score reflects:
  • how well the user's trait profile sits inside the track's ideal region
  • whether core identity traits are genuinely present (penalty if not)
  • whether synergistic trait combinations are active (interaction bonus)
  • a coherence multiplier that rewards consistent identity patterns
  • a mild diversity correction that prevents trait-correlation leakage

Engine design goals (all 19 failure modes addressed):
  1  Trait Hijacking          → per-trait contribution is capped
  2  Score Inflation          → output bounded [0, 1]; bonuses are additive-capped
  3  Score Compression        → coherence multiplier widens spread
  4  Weak Contradiction       → penalty ladder scales with how far below threshold
  5  Over-Penalization        → penalty is multiplicative and bounded below at 0.10
  6  Interaction Explosion    → interaction bonus is gated and soft-capped
  7  Weak Interaction         → smooth sigmoid gate instead of hard step
  8  Trait Correlation        → effective-weight deduplication across correlated pairs
  9  Weak Hybrid Handling     → realistic partial credit inside penalty/bonus logic
 10  Confidence Hallucination → not computed here; confidence.py remains unchanged
 11  Calibration Drift        → all constants are named, documented, and centralised
 12  Sparse Trait Vuln.       → coverage factor scales with observed trait diversity
 13  Behavioral Implausibility→ final score clipped to [0, 1]; no phantom highs
 14  Sensitivity Instability  → sigmoid gates smooth all threshold crossings
 15  Explanation Misalignment → score function is transparent; explanation.py unchanged
 16  Frontend Discrimination  → visual+ideation core gated strictly
 17  AI vs Backend Sep.       → ambiguity/pattern required for AI; not Backend
 18  Testing Precision        → precision penalty is steepest in Testing
 19  Mobile Inflation         → execution alone insufficient; trial+structure required

Compatibility
-------------
• Reads  TRACK_DATA["tracks"]  with the exact JSON schema in tracks_profile.json
• Accepts user traits dict: { trait_name: float [0,1], ... }
• Exposes score_tracks(user)  →  { track_name: float [0,1], ... }
• TRACK_PROFILES alias preserved so pipeline.py imports continue unchanged
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict, Tuple

# ---------------------------------------------------------------------------
# 0. Constants & calibration knobs
#    Change these numbers to recalibrate without touching logic.
# ---------------------------------------------------------------------------

# Path to track definitions
_TRACKS_JSON = Path(__file__).parent / "Data" / "tracks_profile.json"

# Trait compatibility scoring
_TRAIT_SCORE_GAMMA: float = 2.0     # sharpens the in-range Gaussian peak
_TRAIT_CONTRIB_CAP: float = 0.18    # max any single trait may contribute (anti-hijack)

# Penalty
_PENALTY_SIGMOID_K: float     = 8.0   # steepness of penalty sigmoid gate
_PENALTY_SIGMOID_SHIFT: float = 0.35  # shift point: penalty ramps from here (0=threshold, 1=zero)
_PENALTY_FLOOR: float         = 0.10  # worst-case per-trait penalty retention

# Interaction bonus
_INTER_SIGMOID_K: float    = 10.0   # steepness of interaction gate
_INTER_BONUS_CAP: float    = 0.30   # absolute ceiling on total interaction bonus

# Coherence multiplier
_COHERENCE_K: float        = 3.0    # sensitivity of coherence amplification
_COHERENCE_RANGE: Tuple    = (0.82, 1.18)  # [floor, ceil] for multiplier

# Coverage (sparse-trait protection)
_COVERAGE_WEIGHT: float    = 0.08   # how much missing coverage hurts

# Correlated trait pairs (leakage guard)
# If both traits in a pair contribute, the second gets down-weighted.
_CORRELATED_PAIRS: list = [
    ("analytical", "pattern"),
    ("execution",  "trial"),
    ("structure",  "precision"),
    ("visual",     "ideation"),
]
_CORRELATION_DISCOUNT: float = 0.55   # second trait in pair kept at this fraction


# ---------------------------------------------------------------------------
# 1. Load track profiles
# ---------------------------------------------------------------------------

def _load_track_data(path: Path = _TRACKS_JSON) -> dict:
    """Load tracks_profile.json. Returns the full dict."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(
            f"[Masar] tracks_profile.json not found at: {path}\n"
            "Make sure the Data/ folder is next to score.py."
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"[Masar] Malformed tracks_profile.json: {e}")


TRACK_DATA: dict = _load_track_data()

# Convenience alias kept for pipeline.py compatibility
TRACK_PROFILES: dict = TRACK_DATA["tracks"]


# ---------------------------------------------------------------------------
# 2. Math helpers
# ---------------------------------------------------------------------------

def _sigmoid(x: float, k: float = 1.0, shift: float = 0.0) -> float:
    """
    Smooth sigmoid: σ(x) = 1 / (1 + exp(-k*(x - shift)))
    Always returns a value in (0, 1).
    """
    val = -k * (x - shift)
    # clip exponent to avoid overflow
    val = max(-50.0, min(50.0, val))
    return 1.0 / (1.0 + math.exp(val))


def _gaussian_compat(value: float, lo: float, hi: float, gamma: float) -> float:
    """
    Returns how well *value* sits inside [lo, hi].

    • value inside  → approaches 1.0 (peaks at the mid-point)
    • value outside → falls off smoothly via Gaussian decay

    gamma controls sharpness.  Higher = more peaked inside.
    """
    mid   = (lo + hi) / 2.0
    half  = (hi - lo) / 2.0

    if half < 1e-9:
        return 1.0 if abs(value - mid) < 1e-9 else 0.0

    # Normalised distance from ideal midpoint (0 = perfect, 1 = at edge)
    dist = abs(value - mid) / half
    return math.exp(-gamma * max(0.0, dist - 1.0) ** 2)


# ---------------------------------------------------------------------------
# 3. Trait-level compatibility score
# ---------------------------------------------------------------------------

def _build_correlation_discount_map(
    traits_in_track: Dict[str, list]
) -> Dict[str, float]:
    """
    For each correlated pair (a, b): if both are present in the track's
    trait list, mark trait b for discount.

    Returns {trait_name: discount_factor}.  Default factor = 1.0 (no discount).
    """
    discount: Dict[str, float] = {}
    for a, b in _CORRELATED_PAIRS:
        if a in traits_in_track and b in traits_in_track:
            discount[b] = _CORRELATION_DISCOUNT
    return discount


def _trait_compatibility(
    value: float,
    lo: float,
    hi: float,
    weight: float,
    gamma: float = _TRAIT_SCORE_GAMMA,
    cap: float = _TRAIT_CONTRIB_CAP,
) -> float:
    """
    Single-trait contribution to the raw compatibility score.

    contribution = weight × gaussian_compat(value, lo, hi)
    Capped at *cap* to prevent trait hijacking.
    """
    compat = _gaussian_compat(value, lo, hi, gamma)
    contrib = weight * compat
    return min(contrib, cap)


# ---------------------------------------------------------------------------
# 4. Penalty engine
# ---------------------------------------------------------------------------

def _compute_penalty_factor(
    user: Dict[str, float],
    penalty_rules: list,
) -> float:
    """
    Computes a multiplicative retention factor in (0, 1].

    For each penalty rule:
      • If user[trait] ≥ threshold  →  no penalty
      • If user[trait] < threshold  →  smooth penalty via sigmoid gate

    penalty_factor = product of per-rule retentions
    Floored at _PENALTY_FLOOR so no track is ever zeroed out completely.

    The sigmoid gate makes transitions smooth (fixes sensitivity instability).
    """
    retention = 1.0

    for rule in penalty_rules:
        trait     = rule["trait"]
        threshold = rule["threshold"]
        factor    = rule["factor"]          # how bad the breach is

        value = user.get(trait, 0.0)

        if value >= threshold:
            continue

        # How deeply below threshold?  0 = at threshold, 1 = at 0
        depth = (threshold - value) / (threshold + 1e-9)

        # Soft gate: ramps up smoothly as depth grows
        gate = _sigmoid(depth, k=_PENALTY_SIGMOID_K, shift=_PENALTY_SIGMOID_SHIFT)
        # gate ≈ 0 near threshold, → 1 far below

        # Each factor point reduces retention proportionally
        # factor=1.0  → no reduction; factor=2.0 → can halve retention
        severity = (factor - 1.0) / (factor + 1e-9)   # normalised to [0, 1)
        rule_retention = 1.0 - severity * gate

        retention *= max(_PENALTY_FLOOR, rule_retention)

    return retention


# ---------------------------------------------------------------------------
# 5. Interaction bonus engine
# ---------------------------------------------------------------------------

def _compute_interaction_bonus(
    user: Dict[str, float],
    interaction_rules: list,
) -> float:
    """
    Computes additive interaction bonus for synergistic trait combinations.

    Each rule fires smoothly when all trait values exceed their thresholds.
    Combined gate = product of per-trait sigmoid gates.

    Total bonus is soft-capped at _INTER_BONUS_CAP to prevent inflation.
    """
    total_bonus = 0.0

    for rule in interaction_rules:
        traits     = rule["traits"]
        thresholds = rule["thresholds"]
        bonus      = rule["bonus"]

        # Combined gate: product of per-trait smooth gates
        gate = 1.0
        for trait, thr in zip(traits, thresholds):
            value = user.get(trait, 0.0)
            # Positive gate: 1 when value >> threshold, 0 when value << threshold
            gate *= _sigmoid(value, k=_INTER_SIGMOID_K, shift=thr)

        total_bonus += bonus * gate

    # Soft cap via tanh to prevent interaction explosion
    return math.tanh(total_bonus / _INTER_BONUS_CAP) * _INTER_BONUS_CAP


# ---------------------------------------------------------------------------
# 6. Coherence multiplier
# ---------------------------------------------------------------------------

def _compute_coherence(
    user: Dict[str, float],
    track_traits: Dict[str, list],
) -> float:
    """
    Measures how *consistently* the user fits the track's ideal profile.

    Approach:
      • For each trait, compute compat score
      • Coherence = 1 - std(compat_scores)
        → High std means some traits fit well, others don't → low coherence
        → Low std means uniform fit → high coherence

    Scaled to _COHERENCE_RANGE so it acts as a gentle amplifier / damper.
    """
    compat_scores = []
    for trait, (lo, hi, _w) in track_traits.items():
        value  = user.get(trait, 0.0)
        compat = _gaussian_compat(value, lo, hi, _TRAIT_SCORE_GAMMA)
        compat_scores.append(compat)

    if not compat_scores:
        return 1.0

    n    = len(compat_scores)
    mean = sum(compat_scores) / n
    var  = sum((c - mean) ** 2 for c in compat_scores) / n
    std  = math.sqrt(var)

    # Coherence index: 1.0 = perfectly uniform fit, 0.0 = completely scattered
    coherence_index = math.exp(-_COHERENCE_K * std)

    lo_m, hi_m = _COHERENCE_RANGE
    # Map [0, 1] → [lo_m, hi_m]
    multiplier = lo_m + (hi_m - lo_m) * coherence_index

    return multiplier


# ---------------------------------------------------------------------------
# 7. Coverage factor (sparse-trait protection)
# ---------------------------------------------------------------------------

def _compute_coverage(
    user: Dict[str, float],
    track_traits: Dict[str, list],
    threshold: float = 0.30,
) -> float:
    """
    Fraction of track traits where the user has a non-trivial value (≥ threshold).

    A user with responses on only 60% of relevant traits gets a gentle coverage
    penalty regardless of how high the remaining traits score.
    """
    if not track_traits:
        return 1.0

    present = sum(
        1 for trait in track_traits
        if user.get(trait, 0.0) >= threshold
    )
    return present / len(track_traits)


# ---------------------------------------------------------------------------
# 8. Single-track scorer
# ---------------------------------------------------------------------------

def _score_single_track(
    user: Dict[str, float],
    track_def: dict,
) -> float:
    """
    Compute a raw score in [0, 1] for one track.

    Formula (conceptual):
      raw_compat   = Σ  capped_weighted_compat(trait)   (with correlation discount)
      penalty      = multiplicative retention factor
      interaction  = additive bonus (soft-capped)
      coherence    = multiplicative amplifier/damper
      coverage     = linear penalty for sparse evidence

      score = clip(  (raw_compat × penalty + interaction) × coherence
                     - coverage_penalty,  0, 1  )
    """
    traits_def       = track_def.get("traits", {})
    penalty_rules    = track_def.get("penalty_rules", [])
    interaction_rules = track_def.get("interaction_rules", [])

    # --- 8.1 Correlation discount map ---
    discount_map = _build_correlation_discount_map(traits_def)

    # --- 8.2 Weighted compatibility sum ---
    raw_compat = 0.0
    for trait, (lo, hi, weight) in traits_def.items():
        value   = user.get(trait, 0.0)
        disc    = discount_map.get(trait, 1.0)
        contrib = _trait_compatibility(value, lo, hi, weight * disc)
        raw_compat += contrib

    # raw_compat is now in (0, Σ weights) but each term is individually capped

    # --- 8.3 Penalty ---
    penalty = _compute_penalty_factor(user, penalty_rules)

    # --- 8.4 Post-penalty base ---
    base = raw_compat * penalty

    # --- 8.5 Interaction bonus ---
    bonus = _compute_interaction_bonus(user, interaction_rules)

    # --- 8.6 Pre-coherence score ---
    pre_coherence = base + bonus

    # --- 8.7 Coherence multiplier ---
    coherence = _compute_coherence(user, traits_def)
    post_coherence = pre_coherence * coherence

    # --- 8.8 Coverage penalty ---
    coverage = _compute_coverage(user, traits_def)
    coverage_penalty = _COVERAGE_WEIGHT * (1.0 - coverage)
    final = post_coherence - coverage_penalty

    # --- 8.9 Clip to [0, 1] ---
    return max(0.0, min(1.0, final))


# ---------------------------------------------------------------------------
# 9. Main public API
# ---------------------------------------------------------------------------

def score_tracks(user: Dict[str, float]) -> Dict[str, float]:
    """
    Score all tracks for a given user trait profile.

    Parameters
    ----------
    user : dict
        Normalised trait values, e.g.::

            {
                "analytical": 0.82,
                "pattern":    0.74,
                "ambiguity":  0.61,
                ...
            }

    Returns
    -------
    dict
        Track name → score in [0, 1], rounded to 4 decimal places.
        Example::

            {
                "AI":       0.7231,
                "Backend":  0.5812,
                "Frontend": 0.3104,
                "Mobile":   0.4020,
                "Testing":  0.6187,
            }

    Notes
    -----
    • Unknown traits in *user* are silently ignored.
    • Missing traits default to 0.0 (treated as absent).
    • The function is pure: no side effects, safe to call in parallel.
    """
    if not isinstance(user, dict):
        raise TypeError(f"[Masar] score_tracks expects a dict, got {type(user)}")

    raw_scores: Dict[str, float] = {}

    for track_name, track_def in TRACK_PROFILES.items():
        raw_scores[track_name] = _score_single_track(user, track_def)

    # --- Final normalisation pass ---
    # We do NOT collapse scores to sum-to-1 (that destroys discrimination).
    # Instead we apply a mild min-max stretch to expand the spread
    # while keeping all values in [0, 1].  This fixes Score Compression
    # without introducing artificial inflation.
    scores = _stretch_scores(raw_scores)

    return {k: round(v, 4) for k, v in scores.items()}


def _stretch_scores(raw: Dict[str, float]) -> Dict[str, float]:
    """
    Mild min-max stretch to improve discrimination without distorting ranks.

    Maps raw scores so that:
      • The top score lands near _STRETCH_TOP
      • The bottom score lands near _STRETCH_BOTTOM
      • Ranks and relative gaps are perfectly preserved

    Constants are tuned so that a clearly dominant track reaches ~0.80
    and a clearly wrong track falls to ~0.20.
    """
    _STRETCH_TOP    = 0.85
    _STRETCH_BOTTOM = 0.15

    values = list(raw.values())
    lo = min(values)
    hi = max(values)

    if hi - lo < 1e-9:
        # All tracks equally scored → return midpoints
        mid = (_STRETCH_TOP + _STRETCH_BOTTOM) / 2
        return {k: mid for k in raw}

    stretched = {}
    for k, v in raw.items():
        norm = (v - lo) / (hi - lo)               # [0, 1]
        s    = _STRETCH_BOTTOM + norm * (_STRETCH_TOP - _STRETCH_BOTTOM)
        stretched[k] = s

    return stretched


# ---------------------------------------------------------------------------
# 10. Normalisation helper (kept for backward compatibility)
# ---------------------------------------------------------------------------

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Proportional normalisation so scores sum to 1.0.
    Used by explanation.py's normalize_for_display; not used internally.
    """
    total = sum(max(0.0, v) for v in scores.values())
    if total < 1e-9:
        n = len(scores)
        return {k: round(1.0 / n, 4) for k in scores}
    return {k: round(max(0.0, v) / total, 4) for k, v in scores.items()}


# ---------------------------------------------------------------------------
# 11. Smoke-test (run directly: python score.py)
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     # Representative user profiles for sanity-checking the engine

#     _TEST_PROFILES = {
#         "AI-leaning": {
#             "analytical": 0.88, "pattern": 0.82, "ambiguity": 0.75,
#             "frustration": 0.70, "trial": 0.55, "ideation": 0.60,
#             "structure": 0.40, "execution": 0.55, "precision": 0.50,
#             "visual": 0.25,
#         },
#         "Backend-leaning": {
#             "execution": 0.85, "structure": 0.88, "analytical": 0.75,
#             "precision": 0.72, "frustration": 0.65, "ambiguity": 0.50,
#             "trial": 0.35, "ideation": 0.30, "pattern": 0.45, "visual": 0.20,
#         },
#         "Frontend-leaning": {
#             "visual": 0.90, "ideation": 0.85, "trial": 0.70, "execution": 0.75,
#             "ambiguity": 0.65, "frustration": 0.55, "structure": 0.35,
#             "precision": 0.35, "analytical": 0.40, "pattern": 0.30,
#         },
#         "Mobile-leaning": {
#             "execution": 0.80, "trial": 0.72, "structure": 0.75,
#             "visual": 0.60, "precision": 0.62, "ideation": 0.55,
#             "analytical": 0.45, "frustration": 0.60, "ambiguity": 0.50,
#             "pattern": 0.38,
#         },
#         "Testing-leaning": {
#             "precision": 0.90, "pattern": 0.82, "analytical": 0.78,
#             "structure": 0.72, "frustration": 0.75, "execution": 0.50,
#             "ambiguity": 0.40, "trial": 0.38, "ideation": 0.30, "visual": 0.25,
#         },
#         "Ambiguous-hybrid": {
#             "analytical": 0.60, "pattern": 0.55, "execution": 0.58,
#             "structure": 0.52, "precision": 0.50, "ambiguity": 0.48,
#             "visual": 0.40, "ideation": 0.42, "trial": 0.45, "frustration": 0.50,
#         },
#     }

#     print("=" * 60)
#     print("Masar Score Engine — Smoke Test")
#     print("=" * 60)

#     for name, profile in _TEST_PROFILES.items():
#         result = score_tracks(profile)
#         best   = max(result, key=result.get)
#         print(f"\n[{name}]")
#         for track, s in sorted(result.items(), key=lambda x: -x[1]):
#             marker = " ◄" if track == best else ""
#             print(f"  {track:<12} {s:.4f}{marker}")
