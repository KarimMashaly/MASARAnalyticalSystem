from traits import normalize_traits
from scoring import score_tracks, normalize_scores, TRACK_PROFILES
from confidence import compute_confidence
from explanation import explain
import json
import random

def read_feature_map(file_path=r"E:\Documents\Masar\Analytical System\MASAR_Analytical_System\Data\feature_map.json"):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def run_pipeline(raw):
    traits = normalize_traits(raw)

    scores          = score_tracks(traits)
    best_track      = max(scores, key=scores.get)
    probs           = normalize_scores(scores)  # softmax
    confidence_info = compute_confidence(probs)
    explanation     = explain(traits, best_track, probs, confidence_info, TRACK_PROFILES)

    return {
        "traits":      traits,
        "scores":      scores,
        "track":       best_track,
        "confidence":  confidence_info,
        "explanation": explanation
    }

TRAITS = [
    "analytical","structure","execution","ambiguity",
    "trial","frustration","ideation","precision","visual","pattern"
]

def base_user():
    # توزيع أقرب للواقع
    return {k: random.betavariate(2, 2) for k in TRAITS}

def clamp(x): return max(0, min(1, x))

def noisy(u, s=0.2):
    return {k: clamp(v + random.uniform(-s, s)) for k, v in u.items()}

def gen_user(profile):
    u = base_user()

    if profile == "AI":
        u.update({"analytical":0.85, "pattern":0.8, "ambiguity":0.75, "structure":0.4})
    elif profile == "Backend":
        u.update({"structure":0.85, "precision":0.8, "execution":0.75, "visual":0.3})
    elif profile == "Frontend":
        u.update({"visual":0.85, "ideation":0.8, "trial":0.75, "execution":0.7, "structure":0.35, "precision":0.35})
    elif profile == "Mobile":
        u.update({"execution":0.85, "trial":0.8, "structure":0.75, "visual":0.6, "ideation":0.5, "precision":0.5})
    elif profile == "Testing":
        u.update({"precision":0.9, "analytical":0.8, "pattern":0.75, "ambiguity":0.3})

    return u

def mixed_mobile_backend():
    return {
        "execution": random.uniform(0.7, 0.9),
        "trial": random.uniform(0.6, 0.85),
        "structure": random.uniform(0.6, 0.85),
        "precision": random.uniform(0.55, 0.75),
        "analytical": random.uniform(0.6, 0.8),
        "visual": random.uniform(0.4, 0.6),
        "ideation": random.uniform(0.4, 0.6),
        "frustration": random.uniform(0.5, 0.7),
        "ambiguity": random.uniform(0.4, 0.6),
        "pattern": random.uniform(0.5, 0.7)
    }

def weak_user():
    return {k: random.uniform(0.2, 0.5) for k in TRAITS}


from collections import defaultdict

TRACKS = ["AI","Backend","Frontend","Mobile","Testing"]

def run_batch(N=200):
    confusion = {t: {k:0 for k in TRACKS} for t in TRACKS}
    conf_stats = []  # (is_correct, confidence_score)
    wins = defaultdict(int)

    # Archetype + Noisy
    for t in TRACKS:
        for _ in range(N):
            u = noisy(gen_user(t))
            res = run_pipeline(u)
            pred = res["track"]
            confusion[t][pred] += 1
            wins[pred] += 1

            is_correct = int(pred == t)
            conf_stats.append((is_correct, res["confidence"]["score"]))

    # Mixed (Mobile vs Backend)
    for _ in range(N):
        u = mixed_mobile_backend()
        res = run_pipeline(u)
        wins[res["track"]] += 1
        conf_stats.append((0, res["confidence"]["score"]))  # لا يوجد label صحيح واضح

    # Weak
    for _ in range(N):
        u = weak_user()
        res = run_pipeline(u)
        wins[res["track"]] += 1
        conf_stats.append((0, res["confidence"]["score"]))

    return confusion, conf_stats, wins


def accuracy_per_track(confusion, N):
    acc = {}
    for t in confusion:
        acc[t] = confusion[t][t] / N
    return acc

def bias_score(wins):
    total = sum(wins.values())
    share = {k: v/total for k,v in wins.items()}
    # أكبر حصة - المتوسط
    max_share = max(share.values())
    avg = 1/len(share)
    return max_share - avg, share


def confidence_quality(conf_stats):
    # متوسط confidence للحالات الصحيحة مقابل الخاطئة
    correct = [c for ok,c in conf_stats if ok==1]
    wrong   = [c for ok,c in conf_stats if ok==0]
    return {
        "avg_conf_correct": sum(correct)/len(correct) if correct else 0,
        "avg_conf_wrong":   sum(wrong)/len(wrong) if wrong else 0
    }


def low_conf_rate(conf_stats, threshold=0.3):
    low = sum(1 for _,c in conf_stats if c < threshold)
    return low / len(conf_stats)

def print_confusion(confusion):
    print("\nConfusion Matrix:\n")
    for t in TRACKS:
        print(f"{t} → {confusion[t]}")

def test():
    N = 200
    confusion, conf_stats, wins = run_batch(N)

    print_confusion(confusion)

    acc = accuracy_per_track(confusion, N)
    print("\nAccuracy per track:", acc)

    bscore, share = bias_score(wins)
    print("\nBias score:", round(bscore, 3), " | shares:", share)

    cq = confidence_quality(conf_stats)
    print("\nConfidence quality:", cq)

    lcr = low_conf_rate(conf_stats)
    print("\nLow-confidence rate:", round(lcr, 3))

test()

