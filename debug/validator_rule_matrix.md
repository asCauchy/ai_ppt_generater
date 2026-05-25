# Validator Rule Matrix

Complete rule reference for the Presentation Validator (58 rules across 5 layers).

---

## Layer 1: Structure (S01-S09)

| Rule | Severity | Check | Location |
|------|----------|-------|----------|
| S01 | error | Missing narrative_arc | $.narrative_arc |
| S02 | error | Empty sections array | $.narrative_arc.sections |
| S03 | error | Missing/invalid slide_range | $.narrative_arc.sections[i] |
| S04 | error | slide_range out of bounds | $.narrative_arc.sections[i] |
| S05 | error | slide_range start > end | $.narrative_arc.sections[i] |
| S06 | error | Section overlap | $.narrative_arc.sections[i] |
| S07 | warning | Gap between sections | $.narrative_arc.sections[i] |
| S08 | error | Uncovered slides | $.slides |
| S09 | warning | arc_role sequence violation | $.narrative_arc.sections |

---

## Layer 2: Semantic (M01-M10 + N01-N10 + E01-E04)

### M-Series: Structural Semantic (Original)

| Rule | Severity | Check |
|------|----------|-------|
| M01 | warning | breathing_page intensity ≤ 2 |
| M02 | warning | hook not in last section |
| M03 | warning | CTA not in first section |
| M04 | warning | vision not in first section |
| M05 | warning | conflict not in last section |
| M06 | suggestion | (narrative_role, emotional_role) suspect pair |
| M07 | warning | data_viz has content.data |
| M08 | suggestion | quote has content.quote |
| M09 | suggestion | cover narrative_role = hook |
| M10 | suggestion | thanks narrative_role = CTA/recap/release |

### N-Series: Narrative Role Presence (NEW)

| Rule | Severity | Check |
|------|----------|-------|
| N01 | warning | Hook has ≥1 rhetorical technique (question/contrast/surprise/tension) |
| N01 | suggestion | Hook has only 1 technique — add more |
| N02 | warning | Conflict has ≥2 tension dimensions |
| N02 | warning | Conflict is not balanced pro/con list |
| N03 | warning | Escalation has intensifying language |
| N03 | warning | Escalation intensity > previous slide |
| N03 | suggestion | Escalation intensity > previous (not =) |
| N04 | warning | Release has relief/clarity/hope language |
| N04 | warning | Release has no unresolved crisis language |
| N05 | warning | Vision has ≥2 future dimensions |
| N05 | warning | Vision is not describing current state |
| N06 | warning | CTA has ≥2 action techniques |
| N06 | warning | CTA is not summary-disguised-as-CTA |
| N07 | suggestion | Content matches ≥ min required pattern groups for role |
| N08 | warning | Content has no forbidden pattern for role |
| N09 | suggestion | Structural role at expected position |
| N10 | warning | Structural role compatible with narrative role |

### E-Series: Emotional Alignment (NEW)

| Rule | Severity | Check |
|------|----------|-------|
| E01 | warning | emotional_role keywords found in content |
| E01 | warning | No forbidden patterns for declared emotion |
| E02 | warning | emotional_role not contradictory to rhythm.emotional_state |
| E02 | suggestion | emotional_role aligned with rhythm.emotional_state |
| E03 | suggestion | (narrative_role, emotional_role) not suspect pair |
| E04 | suggestion | No jarring emotional transition between slides |

---

## Layer 3: Relation (R01-R05)

| Rule | Severity | Check |
|------|----------|-------|
| R01 | warning | First slide relation_to_prev = null |
| R02 | warning | Last slide relation_to_next = null |
| R03 | warning | Bidirectional consistency (next vs prev) |
| R04 | warning | escalation → release has pivot/breathing_page |
| R05 | suggestion | echo has thematic reference to first half |

---

## Layer 4: Rhythm (Y01-Y10)

| Rule | Severity | Check |
|------|----------|-------|
| Y01 | error | rhythm_map covers all slides |
| Y02 | warning | pause_after=true → pace=slow/pause |
| Y03 | warning | estimated_seconds ≥ 10s |
| Y04 | suggestion | estimated_seconds ≤ 300s |
| Y05 | warning | intensity jump ≤ 2 between adjacent |
| Y06 | suggestion | max intensity ≥ 4 (has climax) |
| Y07 | suggestion | intensity not completely flat |
| Y08 | warning | total time ≥ 70% of declared |
| Y09 | warning | total time ≤ 130% of declared |
| Y10 | suggestion | No jarring emotional_state transition |

---

## Layer 5: Design (D01-D10)

| Rule | Severity | Check |
|------|----------|-------|
| D01 | warning | design_system present |
| D02 | error | Palette colors are valid hex |
| D03 | warning | Typography scale ≥ 4 levels |
| D04 | warning | layout_mode + media_weight compatible |
| D05 | suggestion | brand color_role used appropriately |
| D06 | suggestion | Background switch at section boundary |
| D07 | suggestion | emphasis=hero matches strong emotion |
| D08 | suggestion | recap not emphasis=hero |
| D09 | warning | density=sparse → points ≤ 5 |
| D10 | suggestion | density=dense → points ≥ 3 |

---

## Rule Severity Distribution

| Severity | Count | Rules |
|----------|-------|-------|
| error | 8 | S01-S06, S08, Y01, D02 |
| warning | 26 | S07, S09, M01-M05, M07, N01-N06, N08, N10, E01-E02, R01-R04, Y02-Y03, Y05, Y08-Y09, D01, D03-D04, D09 |
| suggestion | 24 | M06, M08-M10, N01(low), N03(low), N07, N09, E02(low), E03-E04, R05, Y04, Y06-Y07, Y10, D05-D08, D10 |

---

## Phase P0 Activation Status

| Series | Before P0 | After P0 | Status |
|--------|-----------|----------|--------|
| S (Structure) | 9 rules, all active | 9 rules | No change |
| M (Semantic-Structural) | 10 rules, all active | 10 rules | No change |
| N (Narrative Presence) | 0 rules | 10 rules | **NEW** |
| E (Emotional Alignment) | 0 rules | 4 rules | **NEW** |
| R (Relation) | 5 rules, all active | 5 rules | No change |
| Y (Rhythm) | 10 rules, all active | 10 rules | No change |
| D (Design) | 10 rules, all active | 10 rules | No change |
| **Total** | **44** | **58** | +14 rules |

All 58 rules are active and generating output. The validator is now a real constraint layer.
