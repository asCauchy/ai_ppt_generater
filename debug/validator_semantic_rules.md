# Validator Semantic Rules

## Architecture

```
core/validator/
├── __init__.py          # PresentationValidator (5-layer engine, 54 rules)
├── types.py             # ValidationIssue, ValidationResult
├── semantic_rules.py    # Narrative role presence checks (N01-N10)
├── emotional_rules.py   # Emotional alignment checks (E01-E04)
├── rhetorical_patterns.py  # Content analysis functions
└── lexicons/
    ├── emotional_vocab.py   # 18 emotional states × keywords/forbidden
    ├── narrative_vocab.py   # 11 narrative roles × required/forbidden patterns
    └── rhetorical_vocab.py  # Pattern detectors (question, contrast, etc.)
```

## Rule Catalog

### N-Series: Narrative Role Presence (NEW — Phase P0)

| Rule | Name | Severity | Trigger |
|------|------|----------|---------|
| N01 | Hook Effectiveness | warning | Hook slide is agenda-style opening with no engagement technique |
| N01 | Hook Effectiveness | suggestion | Hook has only 1 rhetorical technique (advise adding more) |
| N02 | Conflict Depth | warning | Conflict slide is balanced pro/con (positive ≈ negative points) |
| N02 | Conflict Depth | warning | Conflict has <2 tension dimensions (risk/problem/limitation/stakes/tension) |
| N03 | Escalation Continuity | warning | Escalation slide has intensity ≤ previous slide |
| N03 | Escalation Continuity | warning | Escalation lacks intensifying/raising-stakes language |
| N03 | Escalation Continuity | suggestion | Escalation intensity equals previous (no perceived escalation) |
| N04 | Release Validity | warning | Release slide lacks relief/clarity/hope/stability keywords |
| N04 | Release Validity | warning | Release contains unresolved crisis language |
| N05 | Vision Orientation | warning | Vision describes current state, not future |
| N05 | Vision Orientation | warning | Vision has <2 future dimensions (future/possibility/long-term) |
| N06 | CTA Strength | warning | CTA is summary disguised as call-to-action |
| N06 | CTA Strength | warning | CTA has <2 action techniques (verb/audience/imperative) |
| N07 | Role-Content Match | suggestion | Narrative role content matches < required pattern groups |
| N08 | Role Forbidden Pattern | warning | Content contains pattern forbidden for its narrative_role |
| N09 | Structural Role Position | suggestion | Structural role at unexpected position |
| N10 | Structural-Role-Narrative Conflict | warning | Structural role incompatible with narrative role |

### E-Series: Emotional Alignment (NEW — Phase P0)

| Rule | Name | Severity | Trigger |
|------|------|----------|---------|
| E01 | Emotional-Content Alignment | warning | Emotional_role has no matching keywords in content text |
| E01 | Emotional-Content Alignment | warning | Content contains forbidden pattern for declared emotion |
| E02 | Emotional-State Alignment | warning | emotional_role contradicts rhythm.emotional_state |
| E02 | Emotional-State Alignment | suggestion | emotional_role differs from rhythm.emotional_state |
| E03 | Narrative-Emotional Compatibility | suggestion | (narrative_role, emotional_role) is a suspect pair |
| E04 | Emotional Transition | suggestion | Jarring emotional transition between adjacent slides |

### M-Series: Semantic Structure (EXISTING — enhanced)

| Rule | Name | Severity | Trigger |
|------|------|----------|---------|
| M01 | Breathing Page Intensity | warning | breathing_page intensity > 2 |
| M02 | Hook Position | warning | Hook in last section |
| M03 | CTA Position | warning | CTA in first section |
| M04 | Vision Position | warning | Vision in first section |
| M05 | Conflict Position | warning | Conflict in last section |
| M06 | Narrative-Emotional Suspect | suggestion | (narrative_role, emotional_role) in suspect list |
| M07 | Data Viz Content | warning | presentation_role=data_viz but no content.data |
| M08 | Quote Content | suggestion | presentation_role=quote but no content.quote |
| M09 | Cover Narrative Role | suggestion | Cover page narrative_role != hook |
| M10 | Thanks Narrative Role | suggestion | Thanks page narrative_role not CTA/recap/release |

### Y-Series: Rhythm (EXISTING)

Y01-Y10: intensity jumps, pause/pace coherence, time budget, emotional transitions.

### R-Series: Relation (EXISTING)

R01-R05: bidirectional consistency, escalation→release pivot, echo detection.

### D-Series: Design (EXISTING)

D01-D10: palette, typography, layout/media compatibility, density/emphasis checks.

## How Rules Work

### Narrative Role Presence (N01-N06)

Each rule checks whether the declared `narrative_role` is **genuinely realized** in the slide content:

1. Extract all text (title + subtitle + lead + points)
2. Attempt to match keyword/pattern groups specific to the role
3. Count matched groups vs. required minimum
4. Check for forbidden patterns that neutralize the role
5. Issue warning/suggestion when content doesn't support the role

**Example**: A slide with `narrative_role: "conflict"` must have at least 2 of: risk language, problem language, tension language, limitation language, or stakes language. If it has 0-1, it's flagged. If points split evenly between "breakthroughs" and "challenges", it's flagged as balanced pro/con.

### Emotional Alignment (E01-E04)

Each rule cross-references declared emotional states with actual content:

1. `E01`: Check if `emotional_role` keywords appear in content text
2. `E02`: Compare `emotional_role` against `rhythm.emotional_state` equivalence classes
3. `E03`: Check `(narrative_role, emotional_role)` against known suspect pairs
4. `E04`: Check emotional transitions between adjacent slides

### Lexicon Design

All lexicons are Chinese-language keyword dictionaries:
- **Strong keywords**: High-confidence emotional/narrative indicators
- **Weak keywords**: Supportive evidence (not sufficient alone)
- **Forbidden patterns**: Patterns that neutralize or contradict the role

No embeddings, no classifiers, no external APIs. Pure regex + keyword matching.

## Validation Output Format

```json
{
  "layer": "semantic",
  "rule": "N02",
  "severity": "warning",
  "message": "Conflict slide is a balanced pro/con list — lacks genuine tension",
  "location": "$.slides[4]",
  "context": {
    "narrative_role": "conflict",
    "issue": "balanced_procon_structure",
    "content_excerpt": "..."
  }
}
```

## Rule Count

| Category | Before (Phase 0) | After (Phase P0) |
|----------|-----------------|-------------------|
| Structure (S) | 9 | 9 |
| Semantic (M+N+E) | 10 | 24 |
| Relation (R) | 5 | 5 |
| Rhythm (Y) | 10 | 10 |
| Design (D) | 10 | 10 |
| **Total** | **44** | **58** |

14 new semantic rules added in Phase P0.
