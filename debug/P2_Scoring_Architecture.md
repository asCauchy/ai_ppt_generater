# P2 Scoring Architecture

## Presentation Quality Scoring Engine

---

## 1. Architecture Overview

```
Validator (Constraint Layer)          Scoring Engine (Evaluation Layer)
─────────────────────────────        ────────────────────────────────
Binary correctness checks             Continuous quality gradients
errors / warnings / suggestions       quality_score { overall, dimensions }
"Is this valid?"                      "How good is this?"
```

The Scoring Engine sits **above** the Validator. It does not block, retry, or constrain — it **evaluates**. The two layers are independent:
- A presentation can pass validation with low quality scores
- A presentation can have high quality scores with minor validation warnings
- Only the validator gates the pipeline; the scorer informs.

---

## 2. Scoring Dimensions

### 2.1 Dimension 1: Narrative Force (weight: 0.20)

**What it measures**: How strongly narrative roles are realized in actual content.

**Formula**:
```
narrative_force = AVG(role_realization_scores) + escalation_bonus + cta_bonus

Where:
  role_realization = MIN(100, (matched_pattern_groups / required_groups) * 85 + 15)
  matched_pattern_groups = count of pattern groups (question, contrast, tension, etc.) found in slide text
  escalation_bonus = Σ MIN(15, (intensity_delta * 7)) for each escalation slide
  cta_bonus = Σ (action_techniques * 5) for each CTA slide
```

**Per-role required pattern groups**:
| Role | Pattern Groups | Required |
|------|---------------|----------|
| hook | question, curiosity, contrast, tension, surprising_statement | ≥1 |
| conflict | risk, problem, tension, limitation, stakes | ≥2 |
| escalation | intensifying, raising_stakes, deepening | ≥1 |
| release | relief, clarity, hope, stability | ≥1 |
| vision | future_oriented, imagination, possibility, long_term | ≥2 |
| call_to_action | action_verb, audience_direction, imperative, invitation | ≥2 |
| evidence | data, fact, comparison | ≥1 |
| insight | reframing, deeper_meaning, new_perspective | ≥1 |

**Observed range**: 74-100 (strong)

---

### 2.2 Dimension 2: Emotional Coherence (weight: 0.15)

**What it measures**: How consistent the emotional signals are across the presentation.

**Formula**:
```
emotional_coherence = alignment * 0.40 + continuity * 0.35 + progression * 0.25

Where:
  alignment = (slides where emotional_role == rhythm.emotional_state) / total_slides_with_both * 100
  continuity = 100 - (jarring_transitions_count * 15)
    jarring_transitions ∈ {(solemn,excited), (shocked,relieved), (concerned,relieved), ...}
  progression = MIN(100, unique_emotions * 15 + 30)
    unique_emotions = count of distinct emotional states across all slides
```

**Observed range**: 66-84 (moderate)

---

### 2.3 Dimension 3: Dramatic Tension (weight: 0.15)

**What it measures**: How well the presentation builds and releases dramatic tension.

**Formula**:
```
dramatic_tension = peak_quality * 0.25 + curve_quality * 0.25 + stakes_density * 0.30 + release_payoff * 0.20

Where:
  peak_quality = 100 - abs(peak_position_ratio - 0.65) * 120
    peak_position_ratio = index_of_max_intensity / (total_slides - 1)
    Ideal peak at ~65% through the presentation

  curve_quality = 80 if (strictly rising before peak AND strictly falling after peak)
                = 40 if (rising OR falling but not both)
                = 20 otherwise

  stakes_density = MIN(100, Σ(stakes_keyword_count_per_slide) / n * 15)
    stakes_keywords: 危机|风险|威胁|如果...不|一旦|否则|后果|代价|封锁|制裁|缺口|差距

  release_payoff = MIN(100, 40 + resolution_keyword_count_in_release_slides * 15)
    resolution_keywords: 解决|缓解|改善|化解|克服|突破|转机|出路|希望|曙光
```

**Observed range**: 42-50 (WEAK — universal bottleneck)

---

### 2.4 Dimension 4: Visionary Strength (weight: 0.12)

**What it measures**: How compelling and future-oriented the vision is.

**Formula**:
```
visionary_strength = future_density * 0.30 + scale_score * 0.25 + longterm_score * 0.25 + transform_score * 0.20 + vision_bonus

Where:
  future_density = MIN(100, Σ(future_keywords) * 5)
    future_keywords: 未来|十年|下.*阶段|即将|将会|必将|有望|蓝图|愿景|趋势

  scale_score = MIN(100, Σ(scale_keywords) * 8)
    scale_keywords: 全球|世界|万亿|千亿|颠覆|革命

  longterm_score = MIN(100, Σ(longterm_keywords) * 15)
    longterm_keywords: 十年|二十年|长期|战略|2030|2035

  transform_score = MIN(100, Σ(transform_keywords) * 8)
    transform_keywords: 变革|重塑|重新定义|改写|洗牌|颠覆|突破|跃迁|开创|前所未有

  vision_bonus = +15 per vision slide with future keywords, +10 per vision slide with possibility keywords
```

**Observed range**: 56-100 (high variance — depends on topic/style)

---

### 2.5 Dimension 5: Audience Engagement (weight: 0.13)

**What it measures**: How actively the content engages the audience.

**Formula**:
```
audience_engagement = question_density * 0.25 + contrast_density * 0.30 + surprise_density * 0.25 + address_density * 0.20

Where:
  question_density = MIN(100, Σ(rhetorical_questions) / n * 25)
    question_patterns: ？|吗？|呢？|你想过|有没有想过|为什么

  contrast_density = MIN(100, Σ(contrast_patterns) / n * 30)
    contrast_patterns: 不是...而是|曾经...现在|从...到...的|不再是|看似...实则

  surprise_density = MIN(100, Σ(surprise_patterns) / n * 25)
    surprise_patterns: 竟然|没想到|颠覆|重新定义|前所未有|全球第一

  address_density = MIN(100, Σ(audience_words) / n * 8)
    audience_words: 你|你们|大家|在座|各位
```

**Observed range**: 5-15 (VERY WEAK — Chinese presentations lack audience-directed language)

---

### 2.6 Dimension 6: Rhythm Dynamics (weight: 0.13)

**What it measures**: How dynamic and well-paced the rhythm is.

**Formula**:
```
rhythm_dynamics = pace_variation * 0.25 + pause_quality * 0.30 + climax_score * 0.25 + breathing_score * 0.20

Where:
  pace_variation = MIN(100, unique_pace_values * 35)

  pause_quality = MIN(100, (strategic_pause_ratio * 70) + (MIN(total_pauses, 4) * 7.5))
    strategic_pause: pause_after=true after conflict/escalation/insight/release/CTA slides

  climax_score = MIN(100, max_intensity * 20)

  breathing_score:
    if ≥2 high-intensity slides (intensity ≥4):
      avg_gap = mean distance between high-intensity slides
      score = MAX(30, 100 - abs(avg_gap - 1.5) * 30)
    elif 1 high-intensity slide:
      score = 70  # single peak is fine
    else:
      score = 50
```

**Observed range**: 74-90 (strong — rhythm design is mature)

---

### 2.7 Dimension 7: Cinematic Flow (weight: 0.12)

**What it measures**: How smoothly the presentation flows as a narrative experience.

**Formula**:
```
cinematic_flow = transition_score * 0.25 + momentum_score * 0.30 + order_score * 0.25 + echo_score * 0.20

Where:
  transition_score = MIN(100, unique_relation_types * 20 + 30)
    relation_types: progression, contrast, elaboration, deepening, pivot, echo, etc.

  momentum_score = MIN(100, (building_steps / n * 80) + 20)
    building_step: emotional weight at slide[i] > emotional weight at slide[i-1]
    emotional_weights: {curious:2, focused:3, engaged:4, impressed:5, ..., excited:8, inspired:8}

  order_score:
    If arc_roles match [起,承,转,合]: 25 per matching position (max 100)
    Otherwise: 50 baseline

  echo_score = MIN(100, echo_count * 20 + 30)
    echo: a narrative_role appears more than once (thematic callback)
```

**Observed range**: 67-72 (moderate — transitions work but lack cinematic variety)

---

## 3. Weighting Rationale

| Dimension | Weight | Justification |
|-----------|--------|---------------|
| narrative_force | 0.20 | Core structural quality. Without strong roles, nothing else matters. |
| emotional_coherence | 0.15 | Emotional consistency is the #1 audience trust factor. |
| dramatic_tension | 0.15 | Tension/release is the engine of persuasive presentations. |
| visionary_strength | 0.12 | Important for inspire/persuade goals, less for inform/report. |
| audience_engagement | 0.13 | Directly affects memorability and impact. |
| rhythm_dynamics | 0.13 | Pacing is the invisible hand of presentation quality. |
| cinematic_flow | 0.12 | Story quality — important but emergent from other dimensions. |

Weights sum to 1.00. They can be adjusted per presentation goal (inspire → boost visionary_strength; inform → boost narrative_force).

---

## 4. Sample Outputs

### Run 05 (highest scoring original run): overall=70

```json
{
  "quality_score": {
    "overall": 70,
    "dimensions": {
      "narrative_force": 100,
      "emotional_coherence": 71,
      "dramatic_tension": 50,
      "visionary_strength": 99,
      "audience_engagement": 5,
      "rhythm_dynamics": 86,
      "cinematic_flow": 67
    }
  }
}
```

### Run 04 (lowest scoring original run): overall=61

```json
{
  "quality_score": {
    "overall": 61,
    "dimensions": {
      "narrative_force": 74,
      "emotional_coherence": 83,
      "dramatic_tension": 45,
      "visionary_strength": 56,
      "audience_engagement": 7,
      "rhythm_dynamics": 86,
      "cinematic_flow": 67
    }
  }
}
```

---

## 5. Score Interpretation Guide

| Score | Rating | Description |
|-------|--------|-------------|
| 90-100 | Exceptional | World-class presentation. Rare. |
| 80-89 | Excellent | Strong across all dimensions. Audience will remember this. |
| 70-79 | Good | Solid presentation. Minor weaknesses in 1-2 dimensions. |
| 60-69 | Adequate | Functional but lacks impact. Has clear improvement areas. |
| 50-59 | Weak | Fundamental narrative or engagement issues. Needs significant revision. |
| <50 | Poor | Not presentation-ready. Multiple critical weaknesses. |

---

## 6. Cross-Run Score Distribution

### Original Debug Runs (n=5)

| Dimension | Min | Max | Mean | StdDev |
|-----------|-----|-----|------|--------|
| narrative_force | 74 | 100 | 92.0 | 11.4 |
| emotional_coherence | 66 | 83 | 73.6 | 6.5 |
| dramatic_tension | 44 | 50 | 45.6 | 2.5 |
| visionary_strength | 56 | 99 | 70.8 | 16.8 |
| audience_engagement | 5 | 11 | 8.2 | 2.3 |
| rhythm_dynamics | 86 | 90 | 87.6 | 1.7 |
| cinematic_flow | 67 | 72 | 68.0 | 2.2 |
| **overall** | **61** | **70** | **65.6** | **3.4** |

### Key Observations

1. **dramatic_tension is the universal bottleneck** (mean 45.6, std 2.5) — all presentations lack stakes language and proper tension/release arc
2. **audience_engagement is consistently very low** (mean 8.2, std 2.3) — Chinese AI-generated presentations have almost no audience-directed language
3. **narrative_force is the strongest dimension** (mean 92.0) — the narrative structure is well-implemented
4. **rhythm_dynamics is stable and strong** (mean 87.6, std 1.7) — the rhythm system works reliably
5. **visionary_strength has highest variance** (std 16.8) — depends heavily on topic and NarrativePlanner output

---

## 7. Future ML Upgrade Path

### Phase P2.1: Calibration
- Run 100+ presentations through the scoring engine
- Get human quality ratings (1-5 scale)
- Calibrate dimension weights using linear regression
- Adjust keyword multipliers to minimize MSE vs human ratings

### Phase P2.2: Lightweight Embedding (still no heavy NLP)
- Compute sentence embeddings for slide content using lightweight model (e.g., paraphrase-multilingual-MiniLM)
- Compare content embedding vs narrative_role prototype embedding
- Score = cosine similarity * 100 (continuous, replaces binary pattern matching)

### Phase P2.3: Learned Weights
- Train a small regression model (input: 7 dimension scores, output: human rating)
- Learn per-goal weights (inspire vs persuade vs inform have different optimal weight vectors)
- Deploy as a scikit-learn pipeline (no GPU needed)

### Phase P2.4: Audience Feedback Loop
- If presentations are delivered to real audiences, collect engagement metrics
- Correlate scoring dimensions with actual audience outcomes (retention, persuasion, action)
- Retrain weights to predict real-world effectiveness
