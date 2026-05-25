# Semantic Drift Report

## Executive Summary

A systematic analysis of whether NarrativePlanner's narrative intent is preserved through ContentWriter's output. The semantic drift is **moderate but concentrated** — ContentWriter generally preserves the explicit structural signals (title, narrative_role) while shifting the emotional and semantic weight of content in ways that dilute or redirect the planner's intent.

---

## 1. Drift Detection Methodology

For each run, we compare the NarrativePlanner output (state_02) against the ContentWriter output (state_03), slide by slide, across these dimensions:
- **title** preservation
- **narrative_role** fidelity
- **lead text** semantic alignment with section goal
- **emotional_state** drift (rhythm_map vs. emotional_role)
- **visual_description** alignment with arc_role

---

## 2. Per-Run Drift Analysis

### 2.1 Run 01 — "中国 AI 崛起"

| Slide | NP Intent | CW Output | Drift |
|-------|-----------|-----------|-------|
| 0 (hook) | "从追赶者到定义者" | Points added: patent stats, scene depth | **MILD**: Hook becomes more data-heavy, less mysterious |
| 4 (insight) | "范式跃迁" | 7 detailed points with specific claims | **MODERATE**: NarrativePlanner's "insight" becomes a data-dense lecture slide |
| 5 (recap) | "三大核心论点回顾" | Points repeat earlier slides verbatim | **MODERATE**: Recap degenerates into summary — no new synthesis |

**Key drift at slide 4**: NP intent was "insight" (cognitive shift). CW produced a factual enumeration of 7 achievements. The "aha moment" is flattened into "here are more facts."

### 2.2 Run 02 — "中国 AI 崛起"

| Slide | NP Intent | CW Output | Drift |
|-------|-----------|-----------|-------|
| 3 (insight) | "应用层领跑" from NarrativePlanner | CW adds `emotional_role: "excited"`, detailed case studies | **MILD**: Content aligns well but emotional tone shifts from NP's "engaged" to CW's "excited" |
| 4 (conflict) | "突破与挑战" — NP expects tension | CW splits into 3 "突破" + 3 "挑战" + resolution | **SEVERE**: NP's "conflict" becomes a balanced pro/con list. The tension is symmetrical and resolved within the slide, losing dramatic force |
| 5 (vision) | "全球竞争力" radar chart | CW adds 6-dimension radar with China scores 75-95 vs global avg 40-60 | **MILD**: Vision stays future-oriented but becomes overly quantitative |

**Key drift at slide 4 (conflict → pro/con)**: This is the clearest case of narrative weakening. The NarrativePlanner set `narrative_role: "conflict"` and `relation_to_prev: "contrast"`, signaling dramatic tension. ContentWriter resolved the tension by making both sides equally weighted, losing the narrative function of conflict as a turning point.

### 2.3 Run 03 — "中国 AI 崛起"

| Slide | NP Intent | CW Output | Drift |
|-------|-----------|-----------|-------|
| 2 (evidence) | NP: `pause_after: true` as breathing point | CW adds bar chart data (2018-2024) | **MILD**: Content matches evidence role well |
| 4 (insight) | "全球影响力" — expects perspective shift | CW adds 6 bullet points (TikTok, SenseTime, open source, ISO, BRI) | **MODERATE**: Insight becomes a laundry list of export achievements. "From product output to rule participation" subtitle is stronger than the content that follows |
| 5 (vision) | "下一个十年的关键赛道" | CW adds 5 specific domains (AGI, embodied, AI4Science, autonomous driving, medical) | **MILD**: Future orientation is preserved but becomes domain-checklist rather than visionary |

**Key drift at slide 4**: The NP's `function: "insight"` is implemented as factual enumeration. The cognitive leap from "applications" to "global influence" is asserted rather than revealed.

### 2.4 Run 04 — "中国 AI 崛起"

| Slide | NP Intent | CW Output | Drift |
|-------|-----------|-----------|-------|
| 3 (evidence) | "人才与算力：中国AI的双引擎" | CW adds "200万 researchers, 1.5x US", "东数西算" | **MILD**: Content is faithful to evidence intent |
| 4 (insight) | "应用爆发" — NP expects excitement | CW adds 5 specific cases (Wenxin, BYD, TikTok, industrial, digital humans) | **MODERATE**: Insight becomes case study list. The "重塑全球产业格局" angle is underdeveloped |
| 5 (vision) | "全球影响力：中国AI的出海与标准制定" | CW adds "PaddlePaddle / MindSpore open source, ISO/IEC, BRI" | **MODERATE**: Vision morphs into "current global footprint" rather than "future vision" |

### 2.5 Run 05 — "中国AI崛起"

| Slide | NP Intent | CW Output | Drift |
|-------|-----------|-----------|-------|
| 4 (conflict) | "芯片封锁与人才缺口" — NP uses `emotional_state: "concerned"` | CW adds 7 points with crisis-to-opportunity arc | **LOW**: This is the best-preserved conflict. CW maintains tension with "chip gap 2-3 generations" and "talent gap 300K+" |
| 5 (vision) | "未来机遇" with `emotional_state: "hopeful"` | CW adds chip roadmap, AGI, AI+manufacturing, policy commitments | **MILD**: Vision is well-articulated with timeframe and specific milestones |

**Run 05 is the strongest run** in terms of semantic fidelity. The conflict-vision sequence has genuine emotional trajectory.

---

## 3. Cross-Run Drift Patterns

### 3.1 Generic Explanation Drift

**Affected slides**: 11/35 (31%)

ContentWriter frequently replaces NP's concise, tension-bearing leads with longer, more generic explanations. Example pattern:

```
NP lead: "中国AI已从应用创新走向基础创新，开始引领全球技术方向。"
CW result: Adds 7 bullet points, diluting the single sharp insight into a list.
```

### 3.2 Emotional Collapse

**Affected slides**: 8/35 (23%)

Where NP sets a specific emotional state in `rhythm_map`, CW introduces a new field `emotional_role` that sometimes contradicts:

| Run | Slide | NP rhythm emotion | CW emotional_role | Conflict? |
|-----|-------|-------------------|-------------------|-----------|
| 01 | 3 | confident | reflective | YES — confidence vs. reflection |
| 01 | 4 | inspired | surprised | PARTIAL — inspiration vs. surprise |
| 02 | 3 | engaged | excited | PARTIAL — intensity mismatch |
| 02 | 4 | surprised | skeptical | YES — NP expects wonder, CW delivers doubt |
| 03 | 3 | convinced | reflective | YES — conviction vs. reflection |
| 03 | 5 | inspired | inspired | NO — aligned |
| 04 | 5 | inspired | inspired | NO — aligned |
| 05 | 4 | concerned | concerned | NO — aligned |

**Emotional alignment rate: 3/8 (37.5%)** — meaning CW's emotional_role conflicts with NP's intended emotional_state in 5 of 8 comparable positions.

### 3.3 Narrative Weakening

**Most affected narrative_role**: `conflict`

Only 2 runs (02, 05) use `conflict`, but in run_02 it is severely weakened into a balanced pro/con. This pattern suggests ContentWriter has a tendency to "resolve" tension rather than sustain it.

### 3.4 Semantic Flattening

**Most affected narrative_role**: `insight`

In 5/5 runs, `insight` slides are implemented as bullet-point lists rather than perspective-shifting moments. The structural function of "insight" (cognitive re-framing) is not realized in content.

---

## 4. Drift Severity Summary

| Dimension | Severity | Affected Runs | Affected Slides |
|-----------|----------|---------------|-----------------|
| Emotional role conflict | HIGH | 01, 02, 03 | 5/8 comparable |
| Conflict weakening | HIGH | 02 | 1/2 conflict slides |
| Insight flattening | MEDIUM | All 5 | 5/5 insight slides |
| Generic explanation | MEDIUM | All 5 | 11/35 (31%) |
| Vision → current-state drift | LOW | 04 | 1/5 vision slides |
| Title preservation | NONE | All 5 | 0/35 slides |

---

## 5. Probable Root Causes

1. **ContentWriter prompt lacks "sustain tension" instruction**: CW treats all slides as content-delivery tasks, not dramatic beats. It doesn't know when to hold back.

2. **No emotional_state handoff contract**: CW receives `rhythm_map[i].emotional_state` but independently generates `emotional_role` without reconciling the two.

3. **No dramatic function awareness**: CW doesn't distinguish between "evidence" (present facts), "insight" (reframe perspective), and "conflict" (sustain tension) — it treats all as variations of "explain with points."

4. **Absence of a ContentValidator**: There is no post-write check that measures semantic fidelity against narrative intent. The current validator checks structure, not semantics.
