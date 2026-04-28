# 🚀 Masar – Behavior-Driven Track Recommendation System

---

## 📌 Overview

**Masar** is an intelligent decision system that recommends the most suitable programming track based on **behavioral patterns**, not direct skill input.

Instead of asking:

> “What are you good at?”

Masar asks:

> “How do you think, react, and solve problems?”

Then converts those behaviors into structured traits and maps them to the most compatible technical track.

---

## 🎯 Supported Tracks

* 🧠 Artificial Intelligence (AI)
* ⚙️ Backend Development
* 🎨 Frontend Development

---

## 🧠 System Architecture

The system operates as a **multi-stage pipeline**:

```text
Answers → Traits → Scores → Probabilities → Confidence → Explanation
```

---

# 🧩 Stage 1: Behavioral Input → Traits

## 📋 Questions

Users answer scenario-based questions (real-world situations, not technical questions).

These capture:

* Thinking style
* Decision-making patterns
* Learning behavior
* Reaction to uncertainty and difficulty

---

## ⚙️ Feature Mapping

Each answer contributes to multiple traits:

```text
Answer → Trait adjustments (positive / negative)
```

---

## 🧮 Trait Construction

Implemented in: `traits.py` 

### Steps:

1. Initialize baseline traits
2. Apply feature map effects
3. Normalize traits into range [0, 1]

---

## 🔬 Normalization

Traits are normalized using **bounded linear scaling + clamping**:

```text
raw → normalized ∈ [0, 1]
```

✔ Prevents extreme values
✔ Keeps traits comparable
✔ Stabilizes downstream scoring

---

# 🧠 Stage 2: Traits → Track Scoring

## 📁 Track Profiles

Defined in:

```text
Data/tracks_profile.json
```

Each track includes:

* Trait ranges (min, max)
* Trait weights (importance)
* Penalty rules (constraints)
* Interaction rules (trait synergy)

---

## ⚙️ Scoring Engine

Implemented in: `scoring.py` 

---

### 1) Range-Based Similarity

Each trait is evaluated using a **centered similarity function**:

```text
Similarity = distance from optimal range center
```

✔ Rewards alignment
✔ Penalizes deviation smoothly

---

### 2) Base Score

```text
Base = Σ (weight × similarity)
```

---

### 3) Penalty System (Critical Constraints)

```text
Penalty ∝ (threshold - value)^2
```

✔ Strongly penalizes missing core requirements
✔ Non-linear (small gaps → small penalty, big gaps → strong penalty)

---

### 4) Interaction Bonuses (Synergy)

Captures trait combinations:

```text
Analytical + Ambiguity → AI boost
```

Supports:

* Full bonus
* Partial bonus (near-threshold behavior)

---

### 🎯 Final Score

```text
Score = Base - Penalty + Interaction
```

---

## ⚠️ Important Design Note

Scores are **not bounded** and may be:

* Negative
* Greater than 1

They represent **relative suitability (energy)**, not probabilities.

---

# 🔄 Stage 3: Scores → Probabilities

## Softmax Normalization

Implemented in `scoring.py` 

```text
score → exp(score) / Σ exp(score)
```

---

## Why Softmax?

Converts raw scores into:

* ✔ Probabilities (0 → 1)
* ✔ Comparable values
* ✔ Meaningful distribution

---

## Interpretation

| Concept     | Meaning              |
| ----------- | -------------------- |
| Score       | Suitability strength |
| Probability | Relative likelihood  |

---

# 📊 Stage 4: Confidence Calculation

Implemented in: `confidence.py` 

---

## Uses 3 signals:

### 1) Absolute Gap

```text
top - second
```

### 2) Entropy (uncertainty)

```text
distribution spread
```

### 3) Dominance

```text
top probability
```

---

## Final Formula

```text
Confidence = 0.6*gap + 0.3*certainty + 0.1*dominance
```

---

## Output

```python
{
  "score": 0.82,
  "label": "high",
  "top_track": "AI",
  "second_track": "Backend"
}
```

---

# 🧠 Stage 5: Explanation Engine

Implemented in: `explanation.py` 

---

## Key Features

### ✔ Decision-aware explanation

Uses same logic as scoring (weights + traits)

---

### ✔ Personalized strengths

Selects traits based on **importance for chosen track**

---

### ✔ “Why this, not that”

Explains why the second track was not chosen

---

### ✔ Adaptive tone

Changes based on confidence:

| Confidence | Tone        |
| ---------- | ----------- |
| High       | Assertive   |
| Medium     | Balanced    |
| Low        | Exploratory |

---

### ✔ Development guidance

Suggests improvement areas relevant to the track

---

# 🔁 Full Pipeline

Implemented in: `pipeline.py` 

```python
answers → traits → scores → probs → confidence → explanation
```

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
├── traits.py
├── scoring.py
├── confidence.py
├── explanation.py
├── pipeline.py
├── main.py
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

Masar combines:

| Layer                | Role                           |
| -------------------- | ------------------------------ |
| Behavioral Questions | Capture real thinking patterns |
| Traits               | Abstract personality           |
| Scoring              | Measure compatibility          |
| Softmax              | Normalize competition          |
| Confidence           | Measure certainty              |
| Explanation          | Justify decision               |

---

# ⚠️ Limitations

* Depends heavily on:

  * Feature map quality
  * Track profile calibration
* Not trained on real user data (rule-based system)
* Sensitive to trait overlap between tracks

---

# 💣 Core Insight

Masar is not just a classifier.

> It is a **decision + justification system**
> that explains *why* a track fits a user—not just *which* one.
