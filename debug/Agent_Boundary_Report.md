# Agent Boundary Integrity Report

## Executive Summary

The two-agent architecture (NarrativePlanner → ContentWriter) shows **clear boundary violations in one direction** — ContentWriter adds fields outside its contract scope. NarrativePlanner stays within its lane. The contract itself is **implicit** (no formal schema enforcement), and ContentWriter consistently adds 4-5 extra fields per slide that belong to neither agent's formal domain.

---

## 1. Contract Definition (Inferred from Code Behavior)

### NarrativePlanner's Domain (per slide)
```
title, subtitle, structural_role, narrative_role, semantic_tags
content.lead
relation_to_prev, relation_to_next
rhythm { intensity, pace, emotional_state, pause_after, estimated_seconds }
design { layout_mode, color_role, density, media_weight, emphasis_level }
provenance { generated_by, generated_at, revised_by: [] }
```

### ContentWriter's Domain (expected)
```
content.points         ← fill-in detail
content.data           ← structured data for charts
content.visual_description ← visual design guidance
provenance.revised_by  ← append self
```

---

## 2. Boundary Violation Inventory

### 2.1 ContentWriter Illegal Writes (Fields CW adds that NP already set)

| Field | Set by NP? | Modified by CW? | Violation? |
|-------|-----------|-----------------|------------|
| title | YES | NO | — |
| subtitle | YES | NO | — |
| structural_role | YES | NO | — |
| narrative_role | YES | NO | — |
| semantic_tags | YES | NO | — |
| relation_to_prev | YES | NO | — |
| relation_to_next | YES | NO | — |
| rhythm.* | YES | NO | — |
| design.* | YES | NO | — |
| provenance.generated_by | YES | NO | — |

**Structural field violations: NONE.** ContentWriter correctly preserves all NP-set fields.

### 2.2 ContentWriter Extensions (Fields CW adds beyond its contract)

ContentWriter adds these fields that exist in **neither** the initial state **nor** the NP output:

| Field | Present in NP output? | Present in CW output? | Runs affected |
|-------|----------------------|-----------------------|---------------|
| `emotional_role` | NO | YES | 5/5 |
| `presentation_role` | NO | YES | 5/5 (not always set) |
| `notes.speaker_notes` | NO | YES | 5/5 |

**These are NOT violations** (CW isn't overwriting NP data), but they represent **unbounded field creation** — CW is generating new semantic dimensions that no validator checks.

### 2.3 Detailed Field Analysis

#### `emotional_role` (added by CW)
```
Run 01 emotional_roles: curious, engaged, convinced, reflective, surprised, determined, inspired
Run 02 emotional_roles: curious, engaged, convinced, excited, skeptical, inspired, determined
Run 03 emotional_roles: curious, engaged, convinced, reflective, surprised, inspired, determined
Run 04 emotional_roles: curious, engaged, convinced, impressed, surprised, inspired, determined
Run 05 emotional_roles: curious, engaged, convinced, surprised, concerned, inspired, determined
```

**Issue**: `emotional_role` is semantically similar to `rhythm.emotional_state` (set by NP) but uses a different vocabulary and sometimes contradicts it. This creates dual emotional truth for each slide.

**Contradiction examples**:
- Run 01, slide 3: NP says `emotional_state: "confident"`, CW says `emotional_role: "reflective"` — these evoke different speaker tones
- Run 02, slide 4: NP says `emotional_state: "surprised"`, CW says `emotional_role: "skeptical"` — contradictory audience response targets

#### `presentation_role` (added by CW)
```
Values seen: "data_viz", "process", "timeline", "case_study", "comparison", "interaction", null
```

This field describes the presentation technique, which arguably belongs in the design domain (NP's responsibility). It overrides the implicit presentation mode suggested by NP's `design.layout_mode` and `design.media_weight`.

#### `notes.speaker_notes` (added by CW)
```
Always present after CW. Contains delivery instructions.
```

This is a reasonable CW addition — speaker notes naturally emerge from content. However, no validator checks whether speaker notes contradict NP's rhythm instructions.

---

## 3. NarrativePlanner Boundary Analysis

### 3.1 Does NP illegally write content?

**NO.** In all 5 runs, NP writes only `content.lead` — a single sentence. It never writes `content.points`, `content.data`, or `content.visual_description`. This is clean adherence to its contract.

### 3.2 Does NP set fields it shouldn't?

**NO.** NP's field set is consistent and bounded: structural planning + rhythm + design + lead sentence.

---

## 4. Contract Weaknesses

### 4.1 Implicit Contract
There is no explicit field ownership schema. The contract is inferred from what each agent happens to write. This means:
- If CW starts writing `title` tomorrow, nothing stops it
- If NP starts writing `content.points`, nothing stops it

### 4.2 Emotional Duality
The coexistence of `rhythm.emotional_state` (NP) and `emotional_role` (CW) on the same slide creates an unresolved semantic conflict. No rule specifies which takes precedence.

### 4.3 Unbounded Extension
CW can add arbitrary fields (`emotional_role`, `presentation_role`, `notes`) with no schema validation. This is extensible but ungoverned.

### 4.4 Provenance Tracking
The `provenance.revised_by` array correctly records CW's participation, but does not track *which fields* were modified. This makes it impossible to detect field-level overwrites.

---

## 5. Cross-Run Field Stability

| Field | Setter | Cross-Run Consistency | Notes |
|-------|--------|----------------------|-------|
| title | NP only | 100% consistent with NP output | Never modified by CW |
| narrative_role | NP only | 100% consistent | Never modified |
| rhythm | NP only | 100% consistent | Never modified |
| design | NP only | 100% consistent | Never modified |
| emotional_role | CW only | Present in all CW outputs | CW-invented field |
| presentation_role | CW only | Present, sometimes null | CW-invented field |
| notes | CW only | Always present | CW-invented field |
| content.points | CW only | 28/35 slides have points (80%) | Some content slides use data instead |
| content.data | CW only | 12/35 slides (34%) | Only on data-heavy slides |
| content.visual_description | CW only | 34/35 slides (97%) | Nearly universal |

---

## 6. Findings Summary

### Violations Found
- **Direct overwrites of NP fields: 0** — ContentWriter never modifies NP-set structural fields
- **Emotional contradiction: 5 of 8 comparable positions (62.5%)** — CW's emotional_role conflicts with NP's emotional_state

### Contract Gaps
- **No field ownership schema** — contract is implicit/conventional
- **No field-level modification tracking** — provenance is agent-level, not field-level
- **No emotional consistency check** — two emotional systems coexist without reconciliation
- **No schema for CW extensions** — `emotional_role`, `presentation_role`, `notes` are invented without specification

### Assessment
The boundary between agents is **structurally clean** (no illegal field overwrites) but **semantically leaky** (CW introduces conflicting emotional signals). The architecture is a well-behaved pipe-and-filter, but the filters don't share a common semantic vocabulary for emotion.
