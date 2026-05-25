# P4 Aesthetic Design Principles

## Presentation Cinematic Language

---

## Core Philosophy

> A presentation is not a document. It is not a webpage. It is a temporal visual experience — closer to film + stage than to print.

---

## Principle 1: Restraint Over Abundance

**Rule**: Every element on screen must justify its existence. If it doesn't serve the narrative, remove it.

**Implementation**:
- Hook slides: ≤12 words total
- Vision slides: ≤20 words total
- CTA slides: 1 sentence maximum
- Max 2-3 bullet points on sparse slides
- Max 5-7 on dense slides (conflict/escalation only)

**Anti-pattern**: "Let me explain everything on this slide." If the audience is reading, they're not listening.

---

## Principle 2: Hierarchy Through Weight, Not Size

**Rule**: Visual hierarchy should be achieved through weight contrast, not just font size.

**Implementation**:
- Hero titles: weight 800, tracking -0.02em
- Body: weight 400
- Secondary: weight 300, opacity 0.78
- Captions: weight 300, opacity 0.5
- Important keywords within body text: weight 700, accent color

**Anti-pattern**: Using 5 different font sizes to create hierarchy. Use 2-3 sizes max, differentiate with weight.

---

## Principle 3: Space Is an Active Design Element

**Rule**: Negative space is not "empty" — it's the canvas that makes content powerful.

**Implementation**:
- Hook slides: 50% whitespace
- Vision slides: 45% whitespace
- CTA slides: 55% whitespace
- Conflict slides: 12% whitespace (density creates pressure)
- Never fill the canvas. Content should float in space.

**Anti-pattern**: Filling the slide. If content touches edges or fills available space, the design has failed.

---

## Principle 4: One Focal Point Per Slide

**Rule**: The viewer's eye should land on exactly one place first. Everything else is secondary.

**Implementation**:
- Hook: Center — one big idea
- Evidence: Left-weighted — data leads, viz supports
- Conflict: Fragmented — uneasy gaze path
- Vision: Center with horizon expansion
- CTA: Absolute center — nothing else matters

**Anti-pattern**: Equal visual weight across multiple elements. The eye doesn't know where to go.

---

## Principle 5: Color Signals, Not Decorates

**Rule**: Color is a semantic signal. It tells the viewer what to feel.

**Implementation**:
- 1 accent color max in use at any time
- Backgrounds derived from brand primary/secondary (never raw hex)
- Surfaces have depth (gradient + transparency, not flat)
- Text always 4.5:1+ contrast ratio
- Dark backgrounds for tension/conflict
- Light/gradient backgrounds for hope/vision
- Brand backgrounds for hook/CTA

**Anti-pattern**: Rainbow palettes. Multiple accent colors. "This slide needs more color." No it doesn't.

---

## Principle 6: Motion Has Meaning

**Rule**: Animation is not decoration. It communicates emotional state and narrative rhythm.

**Implementation**:
- Curious → delayed reveal (200ms stagger, soft fade)
- Surprised → sudden appear (80ms stagger, rapid scale)
- Concerned → tense reveal (120ms stagger, building pressure)
- Reflective → slow dissolve (400ms stagger, reduced motion)
- Determined → strong enter (100ms stagger, direct impact)

**Anti-pattern**: Everything animates at the same speed. Random bounces and spins. Motion without semantic purpose.

---

## Principle 7: Depth Through Atmosphere

**Rule**: Flat design has no emotional weight. Depth creates immersion.

**Implementation**:
- 4-layer depth system per slide:
  1. Background (gradient + subtle noise)
  2. Ambient (glow sphere, accent line, tension lines)
  3. Content (typography, data, images)
  4. Accent (dust particles, emphasis markers)
- Glass surfaces for data panels (backdrop-filter blur)
- Subtle shadows only on elevated surfaces, never on text

**Anti-pattern**: Flat colors. CSS box-shadows everywhere. No atmospheric elements.

---

## Principle 8: Typography Is the Voice

**Rule**: The typeface choices ARE the brand voice. They should feel intentional, not default.

**Implementation**:
- Title font: bold weight for impact
- Body font: clear, neutral, invisible
- Never more than 2 typefaces
- Consistent vertical rhythm (line-height ratios: 1.05 hero, 1.15 heading, 1.5 body)
- Line length never exceeds 55 characters

**Anti-pattern**: System default fonts with no hierarchy. Text that stretches edge-to-edge.

---

## Principle 9: Asymmetry Creates Interest

**Rule**: Perfect symmetry is predictable. Controlled asymmetry creates visual tension and engagement.

**Implementation**:
- Conflict/Escalation: deliberately unbalanced (1.5fr : 1fr)
- Evidence: left-weighted (1.3fr : 1fr)
- Hook/Vision/CTA: centered (symmetric for impact)
- Dynamic shift: alternating balance for insight slides

**Anti-pattern**: Every slide centered. "Center everything" looks like a template.

---

## Principle 10: Cinematic Timing

**Rule**: The rhythm of reveals IS the presentation's heartbeat.

**Implementation**:
- Apple easing: cubic-bezier(0.22, 0, 0, 1) — decelerate to stop
- Intensity 5: 0.4x speed modifier (urgent)
- Intensity 1: 1.0x speed (breathing)
- Pace "fast": 120ms per point
- Pace "slow": 500ms per point
- Slide transitions: 0.5s fade (progression), 0.15s (contrast), 0.8s (deepening)

**Anti-pattern**: Instant transitions. Linear easing. Uniform timing regardless of content.

---

## The P4 Cinematic Language

Combined, these 10 principles form a machine-readable cinematic design language:

```
STATE FIELD          →  VISUAL DECISION
─────────────────────────────────────────
narrative_role       →  Typography scale + word limit + whitespace ratio + depth layers
emotional_role       →  Motion entrance + stagger timing + kinetic emphasis
rhythm.intensity     →  Animation speed multiplier
rhythm.pace          →  Point reveal duration
design.emphasis      →  Title scale boost
design.layout_mode   →  Grid template
design.color_role    →  Accent application
relation_to_next     →  Slide transition type
structural_role      →  Container structure
design_system        →  CSS custom properties (palette, fonts, spacing)
```

No visual decision is random. Every pixel traces to a state field.
