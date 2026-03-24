# 🚀 Masar – behavior questions based track recommendation system

## 📌 Overview

**Masar** is an intelligent decision system that recommends the most suitable programming track based on user behavior.

Instead of asking users directly about their skills, Masar:

> Infers personality and learning traits from structured behavioral questions,
> then maps them to the most compatible technical track.

---

## 🎯 Supported Tracks

* 🧠 Artificial Intelligence (AI)
* ⚙️ Backend Development
* 🎨 Frontend Development

---

## 🧠 System Pipeline

Masar operates through a two-stage pipeline:

```text
Questions → Traits → Track Decision
```

---

# 🧩 Stage 1: Questions → Traits

## 📋 Questions

Stored in:

```text
Data/Questions.json
```

Each question represents a real-life scenario, for example:

* Dealing with ambiguity
* Handling frustration
* Execution vs thinking
* Learning style

Each answer contributes to one or more traits.

---

## ⚙️ Feature Mapping

Stored in:

```text
Data/feature_map.json
```

Defines how each answer affects traits:

```text
Answer → Trait Adjustments (± values)
```

---

## 🧮 Trait Construction

Implemented in:

```text
traits.py
```

### Steps:

### 1. Initialize Base Traits

```text
Data/traits.json
```

Acts as a baseline personality profile.

---

### 2. Apply Answer Effects

```text
answers → feature_map → raw traits
```

Each selected answer updates trait values.

---

### 3. Normalize Traits

Using sigmoid normalization:

```text
value → sigmoid → range (0.02 → 0.98)
```

✔ Prevents extreme values
✔ Ensures smooth distribution
✔ Guarantees no trait = 0

---

## 📊 Example Traits Output

```python
{
    "analytical": 0.87,
    "ambiguity": 0.76,
    "execution": 0.71,
    "structure": 0.62,
    "trial": 0.68,
    "frustration": 0.74
}
```

---

# 🧠 Stage 2: Traits → Track Decision

## 📁 Track Profiles

Stored in:

```text
Data/tracks_profile.json
```

Each track defines:

* Trait ranges (min, max)
* Trait importance (weights)
* Penalty rules (constraints)
* Interaction rules (trait combinations)

---

## ⚙️ Scoring Engine

Implemented in:

```text
scoring.py
```

---

### ✅ 1. Base Score (Range Matching)

Measures how well user traits fit expected ranges.

---

### ❌ 2. Penalty (Constraint System)

Applies when critical traits fall below required thresholds.

* Uses nonlinear penalty:

```text
penalty ∝ (gap)^2
```

---

### 🔥 3. Interaction (Trait Synergy)

Boosts score when combinations of traits are strong.

Example:

```text
Analytical + Ambiguity → AI boost
```

---

## 🎯 Final Formula

```text
Final Score = Base Score - Penalty + Interaction Bonus
```

---

## 🏆 Track Selection

Implemented in:

```text
pipeline.py
```

* Highest score → selected track
* Confidence calculated based on score gap

---

# 📊 Confidence

Handled in:

```text
confidence.py
```

Measures how strong the decision is:

* Large gap → high confidence
* Small gap → uncertain recommendation

---

# 🧠 Explanation

Generated in:

```text
explanation.py
```

Produces human-readable output:

* Strengths
* Weaknesses
* Why this track was chosen

---

# 📂 Project Structure

```text
masar/
│
├── Data/
│   ├── feature_map.json
│   ├── Questions.json
│   ├── tracks_profile.json
│   └── traits.json
│
├── traits.py            # Build & normalize traits
├── scoring.py           # Core scoring logic
├── pipeline.py          # Full decision pipeline
├── explanation.py       # Human-readable output
├── confidence.py        # Confidence calculation
├── main.py              # Entry point
│
└── README.md
```

---

# ▶️ How to Run

```bash
python main.py
```

---

# 🧠 Design Philosophy

Masar is built on a hybrid decision model:

| Layer       | Purpose                      |
| ----------- | ---------------------------- |
| Traits      | Represent user behavior      |
| Ranges      | Measure compatibility        |
| Penalty     | Enforce minimum requirements |
| Interaction | Detect strong combinations   |

---

# ⚠️ Important Notes

## 1. Traits Are Not Direct Input

Users do not input traits manually.

> Traits are inferred from behavior.

---

## 2. Accuracy Depends On

* Feature map design
* Track profile calibration

NOT just algorithms.
