"""
confidence.py — Masar Analytical System · Behavioral Confidence Engine
======================================================================

Philosophy
----------
Confidence in Masar is NOT:
    "the top score is higher than the others"

Confidence IS:
    "how behaviorally believable, stable, coherent,
     and recommendation-reliable the result actually is"

The engine is intentionally overlap-aware.

Masar profiles naturally overlap:
    • hybrid identities are normal
    • moderate score gaps may still be meaningful
    • ambiguity is psychologically valid

Therefore:
confidence estimation combines:
    • ranking separation quality
    • top-track strength
    • overlap structure
    • score landscape coherence
    • recommendation stability
    • ambiguity density

This module is:
    • production-safe
    • calibration-ready
    • psychologically conservative
    • smooth (no hard threshold cliffs)
    • resistant to inflated certainty

Compatibility
-------------
Public API preserved:

    compute_confidence(scores: dict) -> dict

Expected input:
    {
        "AI": 0.72,
        "Backend": 0.61,
        ...
    }

Expected output:
    {
        "score": 0.81,
        "label": "high",
        "top_track": "AI",
        "second_track": "Backend"
    }

No pipeline changes required.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

# ============================================================================
# Calibration Constants
# ============================================================================

# --- Separation importance ---
_GAP_WEIGHT: float = 0.34
_RATIO_WEIGHT: float = 0.16

# --- Landscape structure ---
_SPREAD_WEIGHT: float = 0.18
_DOMINANCE_WEIGHT: float = 0.12
_COHERENCE_WEIGHT: float = 0.12

# --- Ambiguity / overlap ---
_OVERLAP_PENALTY_WEIGHT: float = 0.20

# --- Final shaping ---
_CONFIDENCE_GAMMA: float = 0.92

# --- Smooth output bounds ---
_MIN_CONFIDENCE: float = 0.40
_MAX_CONFIDENCE: float = 0.95

# --- Label thresholds ---
_HIGH_THRESHOLD: float = 0.80
_MEDIUM_THRESHOLD: float = 0.65

# --- Numerical safety ---
_EPSILON: float = 1e-9


# ============================================================================
# Utility Functions
# ============================================================================

def _safe_sigmoid(x: float, k: float = 1.0, shift: float = 0.0) -> float:
    """
    Numerically stable sigmoid.

    Returns:
        value in (0, 1)
    """
    z = -k * (x - shift)
    z = max(-50.0, min(50.0, z))
    return 1.0 / (1.0 + math.exp(z))


def _clamp(x: float, lo: float, hi: float) -> float:
    """Clamp x into [lo, hi]."""
    return max(lo, min(hi, x))


def _normalize_scores(values: List[float]) -> List[float]:
    """
    Min-max normalization preserving ranking geometry.

    Returns values in [0, 1].
    """
    lo = min(values)
    hi = max(values)

    if abs(hi - lo) < _EPSILON:
        return [0.5 for _ in values]

    return [(v - lo) / (hi - lo) for v in values]


# ============================================================================
# Signal Extraction
# ============================================================================

def _compute_gap_signal(sorted_scores: List[float]) -> float:
    """
    Measures separation between top-1 and top-2.

    IMPORTANT:
    Masar is overlap-heavy.
    Moderate gaps should still contribute meaningfully.
    """
    top = sorted_scores[0]
    second = sorted_scores[1]

    gap = top - second

    # Smooth saturation
    signal = 1.0 - math.exp(-5.0 * gap)

    return _clamp(signal, 0.0, 1.0)


def _compute_ratio_signal(sorted_scores: List[float]) -> float:
    """
    Measures relative dominance without over-trusting raw gaps.
    """
    top = sorted_scores[0]
    second = sorted_scores[1]

    ratio = top / (second + _EPSILON)

    # Soft normalization
    signal = 1.0 - math.exp(-(ratio - 1.0) * 1.8)

    return _clamp(signal, 0.0, 1.0)


def _compute_spread_signal(scores: List[float]) -> float:
    """
    Measures how differentiated the score landscape is globally.
    """
    n = len(scores)

    if n < 2:
        return 0.0

    mean = sum(scores) / n
    var = sum((s - mean) ** 2 for s in scores) / n
    std = math.sqrt(var)

    # Gentle normalization
    signal = _clamp(std / 0.28, 0.0, 1.0)

    return signal


def _compute_top_strength_signal(sorted_scores: List[float]) -> float:
    """
    Prevents fake confidence from weak overall compatibility.

    High confidence should require:
        not only relative dominance
        but also decent absolute strength.
    """
    top = sorted_scores[0]

    # Smooth activation
    signal = _safe_sigmoid(top, k=8.0, shift=0.52)

    return signal


def _compute_overlap_penalty(sorted_scores: List[float]) -> float:
    """
    Penalizes dense overlap among top tracks.

    Hybrid profiles are allowed.
    But highly compressed landscapes reduce certainty.
    """
    top_cluster = sorted_scores[:3]

    pairwise_gaps = []

    for i in range(len(top_cluster) - 1):
        pairwise_gaps.append(top_cluster[i] - top_cluster[i + 1])

    if not pairwise_gaps:
        return 0.0

    avg_gap = sum(pairwise_gaps) / len(pairwise_gaps)

    # Small gaps -> high penalty
    penalty = math.exp(-8.0 * avg_gap)

    return _clamp(penalty, 0.0, 1.0)


def _compute_coherence_signal(sorted_scores: List[float]) -> float:
    """
    Measures ranking smoothness / landscape plausibility.

    Goal:
        avoid pathological score topologies.

    Example of low coherence:
        0.82, 0.81, 0.20, 0.19, 0.18

    Example of healthier coherence:
        0.82, 0.67, 0.51, 0.38, 0.22
    """
    if len(sorted_scores) < 3:
        return 0.5

    gaps = [
        sorted_scores[i] - sorted_scores[i + 1]
        for i in range(len(sorted_scores) - 1)
    ]

    mean_gap = sum(gaps) / len(gaps)

    if mean_gap < _EPSILON:
        return 0.0

    variance = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
    std = math.sqrt(variance)

    coherence = math.exp(-5.0 * std)

    return _clamp(coherence, 0.0, 1.0)


# ============================================================================
# Confidence Composition
# ============================================================================

def _compose_confidence(
    gap_signal: float,
    ratio_signal: float,
    spread_signal: float,
    top_strength: float,
    coherence_signal: float,
    overlap_penalty: float,
) -> float:
    """
    Combines all confidence signals into final confidence score.
    """

    positive = (
        _GAP_WEIGHT        * gap_signal +
        _RATIO_WEIGHT      * ratio_signal +
        _SPREAD_WEIGHT     * spread_signal +
        _DOMINANCE_WEIGHT  * top_strength +
        _COHERENCE_WEIGHT  * coherence_signal
    )

    negative = (
        _OVERLAP_PENALTY_WEIGHT * overlap_penalty
    )

    raw = positive - negative

    raw = _clamp(raw, 0.0, 1.0)

    # Smooth shaping
    shaped = raw ** _CONFIDENCE_GAMMA

    # Final bounded calibration
    calibrated = (
        _MIN_CONFIDENCE +
        shaped * (_MAX_CONFIDENCE - _MIN_CONFIDENCE)
    )

    return _clamp(calibrated, _MIN_CONFIDENCE, _MAX_CONFIDENCE)


# ============================================================================
# Labeling
# ============================================================================

def _confidence_label(score: float) -> str:
    """
    Confidence labels intentionally overlap-aware.

    high:
        coherent and relatively stable recommendation

    medium:
        meaningful leaning but hybrid / partial overlap exists

    low:
        broad ambiguity or weak recommendation stability
    """
    if score >= _HIGH_THRESHOLD:
        return "high"

    if score >= _MEDIUM_THRESHOLD:
        return "medium"

    return "low"


# ============================================================================
# Public API
# ============================================================================

def compute_confidence(scores: Dict[str, float]) -> Dict[str, object]:
    """
    Compute behavioral confidence for Masar recommendations.

    Parameters
    ----------
    scores : dict
        Track scores in [0, 1].

    Returns
    -------
    dict
        {
            "score": float,
            "label": str,
            "top_track": str,
            "second_track": str
        }

    Notes
    -----
    • Fully overlap-aware
    • Resistant to artificial dominance
    • Smooth transitions
    • Hybrid-compatible
    • Calibration-ready
    """

    if not isinstance(scores, dict):
        raise TypeError(
            f"[Masar] compute_confidence expects dict, got {type(scores)}"
        )

    if len(scores) < 2:
        raise ValueError(
            "[Masar] compute_confidence requires at least 2 tracks."
        )

    # ----------------------------------------------------------------------
    # Ranking
    # ----------------------------------------------------------------------

    sorted_items = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    top_track, top_score = sorted_items[0]
    second_track, _ = sorted_items[1]

    raw_scores = [float(v) for _, v in sorted_items]

    # ----------------------------------------------------------------------
    # Normalize score geometry
    # ----------------------------------------------------------------------

    normalized_scores = _normalize_scores(raw_scores)

    # ----------------------------------------------------------------------
    # Signals
    # ----------------------------------------------------------------------

    gap_signal = _compute_gap_signal(normalized_scores)

    ratio_signal = _compute_ratio_signal(normalized_scores)

    spread_signal = _compute_spread_signal(normalized_scores)

    top_strength = _compute_top_strength_signal(raw_scores)

    overlap_penalty = _compute_overlap_penalty(normalized_scores)

    coherence_signal = _compute_coherence_signal(normalized_scores)

    # ----------------------------------------------------------------------
    # Final confidence
    # ----------------------------------------------------------------------

    confidence = _compose_confidence(
        gap_signal=gap_signal,
        ratio_signal=ratio_signal,
        spread_signal=spread_signal,
        top_strength=top_strength,
        coherence_signal=coherence_signal,
        overlap_penalty=overlap_penalty,
    )

    confidence = round(confidence, 4)

    return {
        "score": confidence,
        "label": _confidence_label(confidence),
        "top_track": top_track,
        "second_track": second_track
    }