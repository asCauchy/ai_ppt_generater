# Reference Distillation Template

> Use this template for analyzing a single reference video segment, frame, or sequence. One file per distilled reference. Store completed distillations in the relevant brand folder alongside the source material.

---

## Metadata

| Field | Value |
|---|---|
| **Source** | [URL / file path / keynote name + year] |
| **Brand** | [Apple / Stripe / Linear / Arc / Motion Studio / Other] |
| **Timestamp** | [MM:SS – MM:SS] |
| **Distillation Date** | [YYYY-MM-DD] |
| **Evaluator** | [name / initials] |
| **Evaluation Score** | ___ / 50 |

---

## What Is This Reference?

[One paragraph: what event, product, or communication is this from? What's the context — keynote opener, feature walkthrough, brand film, product page animation? What makes it worth studying?]

---

## Motion Grammar

Describe the vocabulary of movement used in this segment:

- **Easing philosophy:** [Linear / ease-out dominant / ease-in-out / custom curve / spring-based]
- **Stagger pattern:** [Simultaneous / sequential (describe order) / wave / random / none]
- **Speed range:** [Slow and deliberate / moderate / fast / mixed — describe the range]
- **Key techniques observed:** [e.g., masked reveals, morphing, parallax depth, opacity fades paired with positional moves, etc.]
- **What the motion communicates:** [Weight, precision, playfulness, urgency, calm — what does the movement *feel* like?]

---

## Transition Type

Classify the transition(s) used in this segment:

- **Primary transition:** [Hard cut / dissolve / push / wipe / match-cut / zoom-through / fade-to-color / morph / none — describe]
- **Secondary transition:** [If multiple, note the second type]
- **Bridging elements:** [What (if anything) carries across the transition to maintain continuity?]
- **Spatial logic:** [Does the next scene feel like it exists in the same physical space? A different room? A zoom-in on the same canvas?]
- **Semantic purpose:** [Why this transition type for this content? What does it communicate?]

---

## Composition Pattern

Describe the visual architecture of key frames:

- **Grid structure:** [Symmetrical / asymmetrical / thirds-based / centered / split-screen / full-bleed]
- **Element count:** [How many distinct visual elements in the frame? Minimal (1–3) / moderate (4–7) / dense (8+)]
- **Depth layers:** [Foreground / midground / background — what sits where?]
- **Focal point:** [Where does the eye land first? How is that achieved — scale, contrast, motion, isolation?]
- **Negative space distribution:** [Where is the breathing room? How does it shape the composition?]

---

## Typography Pattern

Describe the type treatment:

- **Font(s):** [Identify or describe — sans-serif geometric, humanist, mono, etc.]
- **Scale range:** [From smallest to largest — e.g., 12px label to 120px hero word]
- **Weight contrast:** [How are weights used to create hierarchy? Regular/Bold only, or multi-weight system?]
- **Reveal behavior:** [How does type enter? Word-by-word, line-by-line, character fade, full block, masked reveal?]
- **Alignment:** [Left / center / right / mixed — and why for each?]
- **Type-motion relationship:** [Does type move? Scale? Stay static while other elements animate around it?]

---

## Emotional Effect

Describe the feeling this reference produces and how it achieves it:

- **Primary emotion:** [Confidence / wonder / precision / warmth / urgency / calm / excitement / gravitas]
- **How it achieves this:** [Through pacing, color, motion weight, music/sound implied timing, type scale, negative space, camera behavior — be specific]
- **Tension profile:** [Constant calm / building intensity / sharp contrast / gentle release / sustained gravity]

---

## Reusable Runtime Abstraction

> This is the most important section. Extract the underlying *pattern* that could be expressed as a reusable motion primitive in our presentation runtime.

- **Pattern name:** [Give it a descriptive name, e.g., "Hero Word Scale-Reveal", "Grid-to-Stack Collapse", "Depth-Push Section Break"]
- **Abstract description:** [Describe the pattern as a parameterized behavior — what are its inputs, what does it produce, what can vary?]
- **Parameters:** [What knobs does this pattern expose? E.g., duration, stagger interval, easing curve, scale range, element count, direction vector]
- **When to use:** [What content type, emotional register, or structural role does this pattern serve?]
- **When NOT to use:** [What would this pattern be wrong for? Where would it feel forced or mismatched?]
- **Known instances:** [Other references that use the same or similar pattern — cross-reference]

---

## Notes

[Anything that doesn't fit the sections above: production details, interesting constraints, historical context, technical implementation hints, related patterns.]
