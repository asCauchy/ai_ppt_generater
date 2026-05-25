# P4 System Architecture

## Cinematic Design Language Engine

---

## 1. Package Structure

```
core/rendering/
├── __init__.py              # Package exports
├── html_renderer.py         # CinematicRenderer (orchestrator, ~650 lines)
├── typography_engine.py     # TypographyEngine — type scale, hierarchy, density
├── composition_engine.py    # CompositionEngine — grids, focal points, negative space
└── theme_engine.py          # ThemeEngine — cinematic surfaces, ambient effects

outputs/
├── p4_cinematic_demo.html   # P4 demo (run_05, 40KB)
└── p4_demo_run02.html       # P4 demo (run_02, conflict + vision)
```

## 2. Engine Responsibilities

### TypographyEngine

**Purpose**: Map state → typographic prescription. Not a font-size picker.

**Input**: slide dict (narrative_role, emotional_role, rhythm.intensity, design.emphasis_level)

**Output**: 
- Type scale selection (title_scale, subtitle_scale, body_scale)
- Weight hierarchy (title_weight 400-800)
- Line height ratios (1.05 hero → 1.5 body)
- Max character width (40-60ch)
- Word limit per slide type
- Content density limits (max_points, max_chars_per_point)
- Kinetic emphasis parameters (delay, easing, keyword highlighting)
- CSS custom properties string for inline styles

**Key Data**: `ROLE_TYPOGRAPHY` dict — 12 narrative roles × full typography prescription.

### CompositionEngine

**Purpose**: Map state → spatial composition. Controls where things go and how much room they have.

**Input**: slide dict, position in deck, total slides

**Output**:
- Scene weight (light → maximum)
- Focal point (center, top-left, asymmetric, fragmented)
- Gaze path (direct, z-pattern, left-to-right, diagonal, expanding)
- Negative space ratio (0.10 → 0.65)
- Asymmetry prescription (symmetric → unbalanced)
- Depth layers (ambient-glow, surface-panel, tension-lines, etc.)
- CSS grid template + areas
- Negative space CSS (vh-based padding)

**Key Data**: `SCENE_WEIGHT`, `FOCAL_POINTS`, `NEGATIVE_SPACE`, `ASYMMETRY`, `LAYERS` — 11 narrative roles × spatial prescription.

### ThemeEngine

**Purpose**: Map state → cinematic surface treatment. Controls atmosphere and depth.

**Input**: design system palette colors

**Output**:
- Cinematic palette (derived from brand colors via darken/lighten)
- Surface treatment per narrative_role (background gradient, text color, glow)
- Ambient effects CSS (glow spheres, tension lines, glass surfaces, noise)
- Layer HTML rendering (generates ambient DOM elements)

**Key Data**: `SURFACE_TREATMENTS` — 11 narrative roles × surface prescription.  
`AMBIENT_CSS` — reusable cinematic effect styles.  
`derive_cinematic_palette()` — algorithmic color derivation.

## 3. Data Flow

```
Presentation State
       │
       ▼
CinematicRenderer.__init__()
  ├── TypographyEngine()
  ├── CompositionEngine()
  └── ThemeEngine(ds_colors)
       │
       ▼
For each slide:
  ├── typography.get_spec(slide)    → type scale, weights, word limits
  ├── typography.css_for_slide()    → CSS custom properties (inline)
  ├── typography.trim_points()      → reduced content density
  ├── composition.get_composition() → spatial prescription
  ├── composition.css_grid_for()    → grid-template
  ├── composition.negspace_css()   → padding, min-height
  ├── theme.get_surface(n_role)    → background, text colors
  └── theme.render_layers()        → ambient DOM elements
       │
       ▼
Single self-contained HTML file
  ├── <style>  — tokens, typography, ambient, motion, transitions
  ├── <section> × N  — slides with inline P4 styles + layers
  └── <script> — navigation + reveal sequencing
```

## 4. P3 vs P4 Comparison

| Dimension | P3 | P4 |
|-----------|----|----|
| Typography | Random scale from design system | Role-driven type scale with word limits |
| Line length | Unlimited | Max 40-60ch per role |
| Title weight | Fixed | 400-800 per role |
| Vertical rhythm | None | Line-height ratios per role + spacing scale |
| Backgrounds | Simple CSS gradients | Derived cinematic palette with noise + glow |
| Negative space | Fixed padding | Per-role whitespace ratio (10-65%) |
| Depth | Flat | 4-layer system (bg → ambient → content → accent) |
| Focal point | None | Per-role gaze path prescription |
| Asymmetry | Centered only | 7 asymmetry modes |
| Content density | All points rendered | Trimmed by intensity + role word limits |
| Surfaces | Plain CSS | Glass, glow, noise, tension lines |
| Color system | Raw palette | Derived cinematic palette (darken/lighten algorithm) |
| Easing | Default ease | Apple cubic-bezier(0.22, 0, 0, 1) |

## 5. Key Design Decisions

### Why inline styles per slide?
Each slide has unique typography and composition parameters. CSS classes can't express per-slide computed values like `--title-size: 64px; --max-width: 40ch; --whitespace-ratio: 0.5`. Inline CSS custom properties are the cleanest way to bind state to style.

### Why algorithmic color derivation?
`derive_cinematic_palette()` applies darken/lighten to brand colors, creating surfaces that always harmonize. No designer needs to manually pick "the dark version of primary" — it's computed.

### Why content density trimming?
The AI generates too much text. The typography engine enforces per-role word limits and per-intensity point counts. This prevents the "wall of text" problem automatically.

### Why ambient layer DOM elements?
CSS-only backgrounds are flat. Glow spheres, tension lines, and accent dust are DOM elements positioned absolutely within the slide. They create depth without images or external assets.

## 6. Scaling Path

### P4.1: Visual Description → AI Image
- Use `content.visual_description` to generate images (DALL-E / Midjourney API)
- Display in visual_placeholder slots
- Cinematic parallax on image backgrounds

### P4.2: Data Visualization
- Render `content.data` as actual charts (CSS bars, SVG radars)
- Animate chart reveals with emotional pacing

### P4.3: Multi-Theme Support
- Theme packs (Apple, Stripe, Linear, Dark, Light)
- Runtime theme switching via CSS custom property swap

### P4.4: Sound Design
- Ambient audio tracks keyed to emotional role
- Transition sounds keyed to relation_to_next
