# 🚀 Masar – Behavior-Driven Track Recommendation System

---

## 📌 Overview

**Masar** is an intelligent decision system that recommends the most suitable programming track based on **behavioral patterns**, not explicit technical input.

Instead of asking:

> “What are your skills?”

Masar infers:

> “How do you think, act, and solve problems?”

Then maps these behavioral traits to the most compatible technical track.

---

## 🎯 Supported Tracks

* 🧠 Artificial Intelligence (AI)
* ⚙️ Backend Development
* 🎨 Frontend Development
* 📱 Mobile Development
* 🧪 Software Testing

---

## 🧠 System Pipeline

```text
Answers → Traits → Scores → Probabilities → Confidence → Explanation
```

---

# 🧩 Stage 1: Answers → Traits

## 📋 Behavioral Questions

Users answer scenario-based questions that capture:

* Thinking style
* Problem-solving approach
* Reaction to ambiguity
* Execution vs planning preference

---

## ⚙️ Feature Mapping

Each answer contributes to traits:

```text
Answer → Trait adjustments
```

---

## 🧮 Trait Construction

Implemented in: `traits.py` 

### Steps:

1. Initialize base traits
2. Apply feature map effects
3. Normalize traits into [0, 1]

---

## 🔬 Trait Normalization

```text
raw → normalized ∈ [0,1]
```

✔ Keeps traits comparable
✔ Prevents extreme values
✔ Stabilizes scoring

---

# 🧠 Stage 2: Traits → Scoring

## 📁 Track Profiles

Defined in:

```text
Data/tracks_profile.json
```

Each track includes:

* Trait ranges (expected behavior)
* Trait weights (importance)
* Penalty rules (minimum requirements)
* Interaction rules (trait combinations)

---

## ⚙️ Scoring Engine

Implemented in: `scoring.py` 

---

### 1) Range-Based Similarity

Each trait is evaluated based on distance from optimal range:

```text
Similarity = closeness to range center
```

---

### 2) Base Score

```text
Base = Σ (weight × similarity)
```

---

### 3) Penalty System

Applied when critical traits are below threshold:

```text
Penalty ∝ (gap)^2
```

✔ Strong nonlinear penalty
✔ Enforces track requirements

---

### 4) Interaction Bonus

Captures synergy between traits:

```text
Analytical + Pattern → AI boost  
Precision + Analytical → Testing boost  
Execution + Visual → Mobile/Frontend boost  
```

Supports:

* Full bonus
* Partial bonus (near-threshold)

---

## 🎯 Final Score

```text
Score = Base - Penalty + Interaction
```

---

## ⚠️ Important

Scores are:

* Not bounded
* May be negative or >1
* Represent **relative suitability**, not probability

---

# 🔄 Stage 3: Scores → Probabilities

## Softmax Normalization

```text
score → exp(score) / Σ exp(score)
```

---

## Purpose

Transforms raw scores into:

* Probabilities (0–1)
* Comparable distribution
* Interpretable output

---

# 📊 Stage 4: Confidence

Implemented in: `confidence.py` 

---

## Signals Used

1. Gap between top and second
2. Entropy (uncertainty)
3. Dominance of top track

---

## Formula

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

## Features

### ✔ Track-aware explanation

Uses actual track weights

---

### ✔ Personalized strengths

Based on relevant traits

---

### ✔ “Why this track”

Explains reasoning behind selection

---

### ✔ “Why not second track”

Handles user doubt explicitly

---

### ✔ Adaptive tone

Changes based on confidence:

| Confidence | Tone        |
| ---------- | ----------- |
| High       | Assertive   |
| Medium     | Balanced    |
| Low        | Exploratory |

---

### ✔ Development suggestions

Guides user toward improvement

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

Masar combines multiple decision layers:

| Layer       | Role                      |
| ----------- | ------------------------- |
| Behavior    | Input signal              |
| Traits      | Abstract representation   |
| Scoring     | Compatibility measurement |
| Softmax     | Relative comparison       |
| Confidence  | Decision certainty        |
| Explanation | Justification             |

---

# ⚠️ Limitations

* Depends on:

  * Feature map design
  * Track profile calibration

* Not data-trained (rule-based system)

* Track overlap may cause:

  * Medium/low confidence results

---

