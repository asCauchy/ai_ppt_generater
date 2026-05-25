# Cinematic Presentation Reference Library

A curated filesystem for collecting and distilling high-end motion presentation references from world-class product communication.

## Brand Sources

| Brand | Why It Matters |
|---|---|
| **Apple** | The gold standard. Spatial continuity, negative space discipline, typographic gravitas, and camera language honed over two decades of keynotes. |
| **Stripe** | Developer-facing motion done right. Restrained palette, typographic precision, and transitions that clarify rather than decorate. |
| **Linear** | Peak modern software branding. Ultra-clean layouts, kinetic typography, and product-aware motion that bridges static UI and cinematic delivery. |
| **Arc** | Browser as theater. Bold compositions, aggressive negative space, and a distinct voice in how they frame software features. |
| **Motion Studio** | Catch-all for boutique motion design studios (Oddfellows, Ordinary Folk, IV, etc.) whose work defines cinematic craft outside the tech keynote genre. |
| **Extracted** | Raw frames, clips, and sequences pulled from references. The raw material before analysis. |

## What Goes in Each Subfolder

### `keynote/`
Full keynote recordings, timestamp indexes, and curated highlight reels. The long-form source material. These are the primary artifacts — everything else is a distillation of moments captured here.

### `transitions/`
Individual transition moments: cuts, wipes, match-cuts, reveals, scene transitions. Focus on how one screen becomes another. The best transitions carry spatial logic — elements don't just swap, they *move* from one arrangement to the next with continuity.

### `typography/`
Type lockups, kinetic type moments, font pairings, scale relationships, and text reveal animations. Includes both static frames (hierarchy study) and motion clips (reveal behavior).

### `layouts/`
Slide-level compositions: grid structures, element placement, figure/ground relationships, and multi-element arrangements. The architecture beneath the content.

### `motion/`
Element-level motion: easing curves, stagger sequences, parallax, morphing, masking reveals, and micro-interactions. The vocabulary of movement — distinct from transitions.

### `compositions/`
Multi-element scenes where layout, typography, and motion converge into a single coherent frame. The highest-level reference: "how does this shot work as a whole?"

## What Makes a Reference High Quality

A reference earns a place here when it demonstrates **intentionality** across multiple dimensions:

- **Cinematic intent** — The motion feels authored, not auto-generated. Someone decided *this* element moves *now* at *this* speed for *this* reason.
- **Structural clarity** — You can reverse-engineer the underlying grid, hierarchy, and motion curve from the output alone.
- **Restraint** — It does less than it could. Every element present has a job. Nothing is decorative.
- **Spatial coherence** — The frame respects consistent spatial rules. Elements don't jump; they travel. Scale changes feel grounded in a virtual camera.
- **Emotional calibration** — The pacing, weight, and rhythm match the content's emotional register. A security slide doesn't bounce. A celebration slide doesn't crawl.
- **Elevated beyond template** — It doesn't look like it came from a deck builder. No clipart cadence, no stock motion presets, no "slide 3 of 24" energy.

## What NOT to Collect

- **Cheap motion graphics** — Pre-built After Effects templates, stock "corporate" animation packs, generic explainer-video motion. If you've seen the same zoom-and-fade on a SaaS landing page and a bank ad, skip it.
- **TikTok/Reels-style effects** — Rapid-fire cuts driven by beat detection rather than narrative logic. Flash frames, capcut transitions, velocity-editing gimmicks. High energy, zero craft.
- **Template-style PPTs** — Standard PowerPoint/Keynote templates. Bullet-list reveals, generic slide transitions, pre-canned chart animations. These are anti-references: they document what we're trying to escape.
- **Decoration without purpose** — Particle systems, glow trails, lens flares, and ambient effects that exist purely to "look dynamic." If removing the effect doesn't break the communication, the effect doesn't belong.
- **UI confetti** — Overloaded product demos where every click triggers a cascade of bounces, spins, and color explosions. This is the opposite of visual restraint.

## Workflow

1. **Collect** — Drop source material into `<brand>/keynote/` or `<brand>/<category>/` as appropriate.
2. **Extract** — Pull specific clips and frames into `extracted/` with source annotations.
3. **Distill** — Use `distillation_template.md` to analyze individual references.
4. **Evaluate** — Score against `reference_evaluation_checklist.md` to separate exemplars from noise.

The goal is not volume. A library of 20 deeply-analyzed references beats 200 unexamined clips.
