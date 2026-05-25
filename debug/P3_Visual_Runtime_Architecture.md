# P3 Visual Runtime Architecture

## State-Driven Cinematic Presentation Engine

---

## 1. Architecture Overview

```
Presentation State
       │
       ▼
┌──────────────────────────────────────────────────┐
│                CinematicRenderer                   │
│                                                    │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ Scene System  │  │Motion System │               │
│  │ (narrative_   │  │ (emotional_  │               │
│  │  role → CSS)  │  │  role → JS)  │               │
│  └──────┬───────┘  └──────┬───────┘               │
│         │                  │                       │
│  ┌──────┴──────────────────┴───────┐               │
│  │     Design Token Binding         │               │
│  │  palette + typography → CSS vars │               │
│  └──────────────┬──────────────────┘               │
│                 │                                   │
│  ┌──────────────┴──────────────────┐               │
│  │    Layout + Typography Engine    │               │
│  │  structural_role → HTML layout   │               │
│  └──────────────┬──────────────────┘               │
│                 │                                   │
│                 ▼                                   │
│       Self-contained HTML file                     │
│   (CSS + JS + 7 slides + transitions)              │
└──────────────────────────────────────────────────┘
```

## 2. State → Visual Mapping

### 2.1 Narrative Role → Scene Template

Each `narrative_role` maps to a distinct visual treatment:

| narrative_role | Scene Container | Background | Alignment | Reveal | Visual Weight |
|---------------|-----------------|------------|-----------|--------|---------------|
| hook | fullscreen-hero | brand-gradient | center | slow-fade-in | high |
| context | overview-grid | neutral | spread | stagger-fade | normal |
| evidence | split-content | light | left-weighted | data-build | high |
| insight | reframe-panel | accent-wash | dynamic | contrast-reveal | high |
| conflict | **tension-split** | **dark-mood** | **asymmetric** | **pressure-build** | **maximum** |
| escalation | intensify-stack | dark-gradient | cascade | escalating-reveal | maximum |
| release | relief-spread | light-wash | balanced | gentle-unfold | normal |
| vision | **horizon-canvas** | **glow-gradient** | **expansive** | **horizon-expand** | high |
| recap | pillars-grid | neutral | structured | pillar-build | normal |
| call_to_action | **focal-center** | **brand-solid** | **center** | **direct-impact** | maximum |

### 2.2 Emotional Role → Motion Language

Each `emotional_role` controls the entrance animation of content elements:

| emotional_role | Entrance | Stagger (ms) | Scale Variation | Description |
|---------------|----------|-------------|-----------------|-------------|
| curious | delayed-reveal | 200 | 0 | Soft, mysterious entrance |
| surprised | sudden-appear | 80 | +5% | Quick, impactful reveal |
| reflective | slow-dissolve | 400 | 0 | Gentle, contemplative |
| confident | strong-enter | 150 | +2% | Bold, stable |
| concerned | tense-reveal | 120 | +3% | Building pressure |
| inspired | rising-reveal | 150 | +4% | Lifting energy |
| excited | burst-reveal | 100 | +6% | High momentum |
| hopeful | warm-fade | 250 | +1% | Gentle optimism |
| determined | resolve-enter | 100 | +3% | Direct, no hesitation |
| engaged | active-reveal | 180 | +1% | Structured engagement |

### 2.3 Rhythm → Animation Pacing

`rhythm.intensity` controls animation speed multipliers:

| Intensity | Duration Multiplier | Effect |
|-----------|-------------------|--------|
| 5 | 0.4x | Fastest — cinematic urgency |
| 4 | 0.55x | Quick build |
| 3 | 0.7x | Moderate pace |
| 2 | 0.85x | Relaxed |
| 1 | 1.0x | Slowest — breathing space |

`rhythm.pace` fine-tunes:
- `fast`: 0.12s per point reveal
- `moderate`: 0.25s
- `slow`: 0.5s

### 2.4 Design Tokens → CSS Custom Properties

All design tokens from `design_system` are bound to CSS custom properties:

```css
:root {
  --color-primary: #003D6B;
  --color-secondary: #5B9BD5;
  --color-accent: #E8A838;
  --color-neutral: #F0F2F5;
  --color-background: #FFFFFF;
  --color-text: #333333;
  --color-text-light: #888888;
  --font-title: '思源黑体';
  --font-body: '微软雅黑';
  --font-hero: 44px;
  --font-display: 56px;
  --spacing-unit: 8px;
  --radius: 12px;
  --transition-speed: 0.6s;
}
```

### 2.5 Relation → Slide Transition

Each `relation_to_next` type maps to a CSS transition class:

| relation | CSS Transition | Duration |
|----------|---------------|----------|
| progression | slide-fade | 0.6s |
| contrast | hard-cut | 0.15s |
| deepening | morph-deepen | 0.8s |
| escalation | intensify | 0.3s |
| pivot | swing-pivot | 0.7s |
| echo | recall-fade | 0.9s |
| emotional_shift | color-shift | 0.6s |

## 3. Scene Design Detail

### Hook Scene (fullscreen-hero)
```
┌─────────────────────────────────────┐
│  ░░░░ brand-gradient ░░░░░░░░░░░░  │
│                                     │
│          TITLE (display size)       │
│          subtitle (light)           │
│          ─── lead ───              │
│                                     │
│    [visual description placeholder] │
│                                     │
└─────────────────────────────────────┘
```
- Font: display size (56px title)
- Centered, minimal elements
- Slow fade-in reveal
- High visual tension

### Conflict Scene (tension-split)
```
┌─────────────────────────────────────┐
│  ▓▓▓▓ dark-mood gradient ▓▓▓▓▓▓▓▓│
│                                     │
│  ║ TITLE (left border: red line)   │
│  ║                                  │
│  ║ • Point 1 ──────────────────────│
│  ║ • Point 2 ──────────── [data]   │
│  ║ • Point 3 ──────────────────────│
│  ║                                  │
└─────────────────────────────────────┘
```
- Dark background (navy → deep blue gradient)
- Red left border on title
- Asymmetric grid (1.3fr : 1fr)
- Red bullets (tension markers)
- Dense text, rapid reveal

### Vision Scene (horizon-canvas)
```
┌─────────────────────────────────────┐
│        glow-gradient                │
│                                     │
│    ═══════ TITLE ═══════           │
│    subtitle centered                │
│                                     │
│    • Point 1 ── glow bullet         │
│    • Point 2 ── glow bullet         │
│    • Point 3 ── glow bullet         │
│                                     │
│         [visual placeholder]         │
│                                     │
└─────────────────────────────────────┘
```
- Bright, expansive
- Centered with large whitespace
- Glowing accent bullets
- Horizon gradient (white → accent wash → brand)

### CTA Scene (focal-center)
```
┌─────────────────────────────────────┐
│  ██████ brand-solid ██████████████ │
│                                     │
│          BIG TITLE                  │
│          (white on brand)           │
│                                     │
│          • Direct point             │
│          • Action point             │
│                                     │
│       [speaker notes hint]          │
│                                     │
└─────────────────────────────────────┘
```
- Solid brand color background
- White text
- Centered, big typography
- Direct impact, no distraction
- Text shadow for depth

## 4. JavaScript Runtime

The HTML includes a minimal (~60 lines) JS runtime:

- **Slide Navigation**: Keyboard (← → Space Home End), click, touch swipe
- **Progress Tracking**: Progress bar + nav dots
- **Content Reveal Sequencing**: Points reveal one-by-one with emotional stagger
- **Transition Management**: CSS class toggling based on relation_to_next

### Point Reveal Sequence

Each point item reveals with a staggered delay:
- `stagger = emotional_motion.stagger * intensity_speed_modifier`
- Points enter with `transform: translateX(12px) → translateX(0)` + opacity 0→1
- Bullet dots scale from 0→1 on reveal

## 5. File Structure

```
core/rendering/
├── __init__.py           # Package exports
└── html_renderer.py      # CinematicRenderer (complete engine)

outputs/
├── demo_runtime.html     # Main demo (run_05, highest scoring)
├── demo_run_01.html      # Run 01 demo
├── demo_run_02.html      # Run 02 demo
├── demo_run_03.html      # Run 03 demo
├── demo_run_04.html      # Run 04 demo
└── demo_run_05.html      # Run 05 demo
```

## 6. Design Principles

1. **Every visual decision traces to a state field** — no random design
2. **Single self-contained HTML file** — no dependencies, no build step
3. **CSS custom properties for all tokens** — runtime-swappable theming
4. **JS is minimal (~60 lines)** — progressive enhancement, not framework
5. **Scene templates are data, not code** — adding a new narrative_role = adding a dict entry

## 7. Scaling Path

### P3-B: More Scene Templates
- Add scene variants per structural_role (cover vs content vs summary have different layout needs)
- Add sub-scenes based on presentation_role (data_viz, timeline, quote)

### P3-C: Rich Data Visualization
- Render `content.data` fields as actual charts (CSS/SVG bar charts, radar charts)
- Animate chart reveals

### P3-D: Real Image Placeholders
- Use `content.visual_description` to generate AI image prompts
- Display generated images in visual_placeholder slots

### P3-E: Export to Video
- Capture HTML slides as frames (puppeteer/playwright)
- Stitch into video with audio narration
- Cinematic transitions become video transitions

## 8. Running the Demo

```bash
cd G:/codes/ai_ppt_generator
python -c "
import json
from core.rendering import render_to_file
with open('debug/run_05/04_state_final.json', 'r', encoding='utf-8') as f:
    state = json.load(f)
render_to_file(state, 'outputs/demo_runtime.html')
print('Open outputs/demo_runtime.html in a browser')
"
```

Open in browser. Use ← → arrow keys or click to navigate. Watch the cinematic reveal sequencing.
