"""Style Compiler — ResolvedVisualConfig → CSS + JS for the renderer.

The compiler translates resolved visual configs into:
  1. CSS custom properties per slide (inline style)
  2. CSS keyframes and class definitions
  3. JavaScript configuration objects for the runtime

The renderer consumes the compiler's output. The compiler makes zero
aesthetic decisions — it purely translates ResolvedVisualConfig fields
into CSS/JS syntax.
"""

from __future__ import annotations

import html as html_mod
from .style_schema import ResolvedVisualConfig, StylePack, SemanticRequirements


class StyleCompiler:
    """Compile resolved visual configs into renderer-consumable CSS and JS."""

    def __init__(self, style_pack: StylePack, resolver=None):
        self.pack = style_pack
        self._resolver = resolver

    # ------------------------------------------------------------------
    # Global CSS (same for all slides)
    # ------------------------------------------------------------------

    def compile_root_css(self) -> str:
        """Generate :root CSS custom properties from the style pack."""
        from .style_resolver import create_resolver
        resolver = self._resolver or create_resolver(self.pack)
        return resolver.css_tokens()

    def compile_ambient_css(self) -> str:
        """Generate ambient surface CSS (glass, glow, noise, etc.)."""
        ss = self.pack.surface_system
        return ss.ambient_css_template.replace(
            "{glass}", self.pack.color_system.surface_glass
        )

    def compile_motion_css(self) -> str:
        """Generate CSS for keyframe animations and entrance classes."""
        ml = self.pack.motion_language
        parts = []

        # Keyframes
        for name, css in ml.keyframes.items():
            parts.append(css)

        # Entrance animation delay classes
        for emotion, spec in ml.emotional_entrance.items():
            entrance_type = spec.get("type", "active_reveal")
            parts.append(
                f".point-item.entrance-{entrance_type} {{ "
                f"transition-delay: calc(var(--item-index) * {spec.get('stagger_ms', 150)}ms); }}"
            )

        # Intensity speed modifiers
        for intensity, mod in ml.intensity_speed.items():
            dur = int(400 * mod.get("duration_mult", 0.7))
            parts.append(
                f".slide.intensity-{intensity} .point-item {{ "
                f"transition-duration: {dur}ms; }}"
            )

        # Pace modifiers
        parts.append(".slide.pace-fast .point-item { transition-duration: 0.12s; }")
        parts.append(".slide.pace-slow .point-item { transition-duration: 0.5s; }")

        return "\n".join(parts)

    def compile_transition_css(self) -> str:
        """Generate CSS for slide-to-slide transitions."""
        tl = self.pack.transition_language
        parts = []

        for relation, spec in tl.relation_transitions.items():
            ttype = spec.get("type", "slide_fade")
            dur = spec.get("duration_ms", 500)
            easing = spec.get("easing", tl.default_easing)
            parts.append(
                f".transition-{ttype} {{ "
                f"transition-duration: {dur}ms; "
                f"transition-easing: {easing}; }}"
            )

        return "\n".join(parts)

    def compile_typography_css(self) -> str:
        """Generate typography CSS classes."""
        return """
.slide-title {
  font-size: var(--title-size, var(--font-h1));
  font-weight: var(--title-weight, 600);
  letter-spacing: var(--title-tracking, -0.01em);
  line-height: var(--line-height-title, 1.1);
  max-width: var(--max-width-ch, 55ch);
  font-family: var(--font-title), var(--font-body), system-ui, sans-serif;
}
.slide-subtitle {
  font-size: var(--subtitle-size, var(--font-body-lg));
  font-weight: var(--subtitle-weight, 400);
  opacity: 0.78;
  max-width: var(--max-width-ch, 55ch);
}
.slide-lead {
  font-size: var(--body-size, var(--font-body));
  font-weight: var(--body-weight, 400);
  line-height: var(--line-height-body, 1.5);
  max-width: var(--max-width-ch, 55ch);
}
.point-item {
  font-size: var(--body-size, var(--font-body));
  font-weight: var(--body-weight, 400);
  line-height: var(--line-height-body, 1.5);
  max-width: var(--max-width-ch, 55ch);
}
.point-item .kw { font-weight: 700; color: var(--c-accent); }
.slide-inner > * + * { margin-top: var(--spacing-unit); }
.content-area > * + * { margin-top: calc(var(--spacing-unit) * 1.5); }
"""

    def compile_layout_css(self) -> str:
        """Generate layout CSS classes."""
        return """
.slide-inner {
  width: 100%; max-width: 1400px; margin: 0 auto;
  display: flex; flex-direction: column;
}
.slide.scene-fullscreen_hero .slide-inner,
.slide.scene-focal_center .slide-inner,
.slide.scene-horizon_canvas .slide-inner {
  max-width: 1000px; text-align: center; align-items: center;
}
.slide.scene-tension_split .slide-inner { justify-content: start; }
.slide.scene-horizon_canvas .slide-inner { justify-content: center; min-height: 70vh; }
.slide.scene-focal_center .slide-inner { justify-content: center; min-height: 70vh; }
.content-area { flex: 1; }
.content-split { display: grid; grid-template-columns: 1fr 1fr; gap: 3vw; align-items: start; }
.content-split.asymmetric { grid-template-columns: 1.3fr 1fr; }
.content-stack { display: flex; flex-direction: column; gap: 0.5em; }
"""

    # ------------------------------------------------------------------
    # Per-slide CSS
    # ------------------------------------------------------------------

    def compile_slide_inline_css(self, cfg: ResolvedVisualConfig) -> str:
        """Generate inline CSS custom properties for a single slide."""
        lines = [
            f"--title-size: {cfg.title_size_px}px;",
            f"--title-weight: {cfg.title_weight};",
            f"--title-tracking: {cfg.title_tracking_em}em;",
            f"--subtitle-size: {cfg.subtitle_size_px}px;",
            f"--body-size: {cfg.body_size_px}px;",
            f"--body-weight: {cfg.body_weight};",
            f"--line-height-title: {cfg.line_height_title};",
            f"--line-height-body: {cfg.line_height_body};",
            f"--max-width-ch: {cfg.max_width_ch}ch;",
            f"padding: {cfg.slide_padding};",
            f"background: {cfg.bg_css};",
            f"color: {cfg.text_color};",
            f"--text-secondary: {cfg.text_secondary_color};",
        ]
        return " ".join(lines)

    def compile_slide_classes(self, cfg: ResolvedVisualConfig) -> list[str]:
        """Generate CSS class list for a slide."""
        classes = [
            "slide",
            f"intensity-{cfg.intensity}",
            f"pace-{cfg.pace}",
            f"emphasis-{cfg.emphasis_level}",
            f"scene-{cfg.container_class}",
        ]
        if cfg.transition_type:
            classes.append(f"transition-{cfg.transition_type}")
        if cfg.accent_glow:
            classes.append("accent-glow")
        return classes

    def compile_slide_data_attrs(self, cfg: ResolvedVisualConfig, index: int) -> str:
        """Generate data-* attributes for the slide element."""
        return (
            f'data-index="{index}" '
            f'data-narrative="{cfg.narrative_role}" '
            f'data-emotional="" '
            f'data-intensity="{cfg.intensity}" '
            f'data-entrance="{cfg.entrance_type}"'
        )

    # ------------------------------------------------------------------
    # JavaScript runtime config
    # ------------------------------------------------------------------

    def compile_js_config(self, total: int) -> str:
        """Generate JavaScript configuration for the presentation runtime."""
        return f"""<script>
// === Presentation Visual Runtime (Style-Compiled) ===
const TOTAL = {total};
let current = 0;
let sequenceTimer = null;

const slides = document.querySelectorAll('.slide');
const dots = document.querySelectorAll('.nav-dot');
const progress = document.getElementById('progress-bar');
const overlay = document.getElementById('overlay');

function showSlide(index) {{
  if (index < 0 || index >= TOTAL) return;

  const oldSlide = slides[current];
  const newSlide = slides[index];

  if (oldSlide) {{
    oldSlide.classList.remove('active');
    oldSlide.classList.add('exiting');
    setTimeout(function() {{ oldSlide.classList.remove('exiting'); }}, 800);
  }}

  newSlide.classList.add('active');
  revealSequence(newSlide);
  current = index;
  updateUI();
}}

function revealSequence(slide) {{
  if (sequenceTimer) clearTimeout(sequenceTimer);

  const points = slide.querySelectorAll('.point-item');
  const intensity = parseInt(slide.dataset.intensity) || 3;
  const entrance = slide.dataset.entrance || 'active_reveal';

  points.forEach(function(p) {{ p.classList.remove('revealed'); }});

  const motionMap = {{{self._js_motion_map()}}};
  const stagger = motionMap[entrance] || 150;
  const speedMod = Math.max(0.4, 1 - (intensity - 1) * 0.15);
  const delay = stagger * speedMod;

  points.forEach(function(p, i) {{
    setTimeout(function() {{ p.classList.add('revealed'); }}, delay * (i + 1));
  }});
}}

function updateUI() {{
  const pct = ((current + 1) / TOTAL) * 100;
  progress.style.width = pct + '%';
  dots.forEach(function(d, i) {{ d.classList.toggle('active', i === current); }});
}}

document.addEventListener('keydown', function(e) {{
  if (e.key === 'ArrowRight' || e.key === 'ArrowDown' || e.key === ' ') {{
    e.preventDefault(); showSlide(current + 1);
  }} else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {{
    e.preventDefault(); showSlide(current - 1);
  }} else if (e.key === 'Home') {{
    showSlide(0);
  }} else if (e.key === 'End') {{
    showSlide(TOTAL - 1);
  }}
}});

dots.forEach(function(dot) {{
  dot.addEventListener('click', function() {{
    showSlide(parseInt(dot.dataset.goto));
  }});
}});

let touchStartX = 0;
document.addEventListener('touchstart', function(e) {{ touchStartX = e.touches[0].clientX; }});
document.addEventListener('touchend', function(e) {{
  const diff = touchStartX - e.changedTouches[0].clientX;
  if (Math.abs(diff) > 50) showSlide(current + (diff > 0 ? 1 : -1));
}});

document.getElementById('slides-container').addEventListener('click', function(e) {{
  if (e.target.closest('.nav-dot')) return;
  if (current < TOTAL - 1) showSlide(current + 1);
}});

showSlide(0);
</script>"""

    def _js_motion_map(self) -> str:
        """Generate the JavaScript motion stagger map."""
        ml = self.pack.motion_language
        entries = []
        for emotion, spec in ml.emotional_entrance.items():
            t = spec.get("type", "active_reveal")
            s = spec.get("stagger_ms", 150)
            entries.append(f"'{t}': {s}")
        return ", ".join(entries)
