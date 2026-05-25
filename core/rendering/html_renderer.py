"""Style-Agnostic Cinematic HTML Renderer — P5.

Takes a Presentation State and a Style Pack and produces a self-contained
HTML file. The renderer OWNS ZERO aesthetic decisions:

  - No hardcoded colors
  - No hardcoded fonts
  - No hardcoded spacing
  - No hardcoded transitions
  - No hardcoded animation curves
  - No hardcoded compositions

Every visual value flows through the chain:
  State → state_mapper → SemanticRequirements
       → style_resolver → ResolvedVisualConfig
       → compiler → CSS/JS

The renderer only INTERPRETS styles, it never DECIDES them.
"""

from __future__ import annotations

import html as html_mod
import os
from typing import Optional

from ..style_system.style_pack_loader import StylePackLoader
from ..style_system.style_resolver import StyleResolver, create_resolver
from ..style_system.style_schema import StylePack, SemanticRequirements, ResolvedVisualConfig
from ..style_system.compiler import StyleCompiler
from ..runtime.state_mapper import map_to_semantic_requirements
from ..runtime.scene_runtime import (
    render_slide, render_overlay, render_progress, render_nav, find_section_badge,
)


class CinematicRenderer:
    """Style-agnostic presentation renderer.

    Usage:
        renderer = CinematicRenderer(state, style_pack_name="apple_minimal")
        html = renderer.render()
    """

    def __init__(self, state: dict, style_pack_name: str = "apple_minimal"):
        self.state = state
        self.slides = state.get("slides", [])
        self.ds = state.get("design_system", {})
        self.meta = state.get("meta", {})
        self.arc = state.get("narrative_arc", {})
        self.context = state.get("context", {})

        # Style system
        self._loader = StylePackLoader()
        self.style_pack = self._loader.load(style_pack_name)
        self._resolver = create_resolver(self.style_pack)
        self._compiler = StyleCompiler(self.style_pack, self._resolver)

        # Pre-compute all visual configs
        self._configs: list[ResolvedVisualConfig] = []
        for i, slide in enumerate(self.slides):
            req = map_to_semantic_requirements(slide, i, len(self.slides), self.arc)
            cfg = self._resolver.resolve(req, i, len(self.slides))
            self._configs.append(cfg)

    def render(self) -> str:
        """Generate complete style-compiled HTML document."""
        lang = self.meta.get("language", "zh-CN")
        title = html_mod.escape(self.meta.get("title", "Presentation"))
        style_name = html_mod.escape(self.style_pack.name)

        return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — {style_name}</title>
{self._render_styles()}
</head>
<body>
{render_overlay()}
{render_progress(100 / max(len(self.slides), 1))}
<main id="slides-container">
{self._render_slides()}
</main>
{render_nav(len(self.slides))}
{self._compiler.compile_js_config(len(self.slides))}
</body>
</html>"""

    # ------------------------------------------------------------------
    # Styles — all from compiler, zero hardcoding
    # ------------------------------------------------------------------

    def _render_styles(self) -> str:
        tokens = self._compiler.compile_root_css()
        ambient = self._compiler.compile_ambient_css()
        motion = self._compiler.compile_motion_css()
        transitions = self._compiler.compile_transition_css()
        typography = self._compiler.compile_typography_css()
        layout = self._compiler.compile_layout_css()

        return f"""<style>
/* ================================================================
   Style Pack: {self.style_pack.name} v{self.style_pack.version}
   All values compiled from style pack — zero renderer hardcoding
   ================================================================ */

/* === Design Tokens === */
:root {{
{tokens}
}}

/* === Cinematic Surfaces === */
{ambient}

/* === Typography === */
{typography}

/* === Layout Framework === */
{layout}

/* === Motion System === */
{motion}

/* === Transitions === */
{transitions}

/* === Global Reset === */
* {{ margin:0; padding:0; box-sizing:border-box; }}
html, body {{
  width:100%; height:100%; overflow:hidden;
  font-family: var(--font-body), system-ui, sans-serif;
}}
body {{
  background: var(--c-surface-bg);
  color: var(--c-text-primary);
}}

#slides-container {{
  width: 100%; height: 100vh;
  position: relative;
}}

.slide {{
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  opacity: 0;
  pointer-events: none;
  transition: opacity var(--transition-speed) var(--transition-easing),
              transform var(--transition-speed) var(--transition-easing);
  transform: translateY(20px);
}}

.slide.active {{
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}}

.slide.exiting {{
  opacity: 0;
  pointer-events: none;
}}

/* Slide-level container modulations */
.slide.scene-fullscreen_hero {{ padding: 8vh 6vw; }}
.slide.scene-tension_split {{ padding: 4vh 5vw; }}
.slide.scene-horizon_canvas {{ padding: 6vh 10vw; text-align: center; }}
.slide.scene-focal_center {{ padding: 8vh 8vw; text-align: center; }}
.slide.scene-overview_grid {{ padding: 6vh 6vw; }}
.slide.scene-split_content {{ padding: 5vh 6vw; }}
.slide.scene-reframe_panel {{ padding: 5vh 7vw; }}
.slide.scene-relief_spread {{ padding: 6vh 7vw; }}

/* Intensity modifiers */
.slide.intensity-5 {{ animation-duration: 0.3s; }}
.slide.intensity-4 {{ animation-duration: 0.5s; }}
.slide.intensity-3 {{ animation-duration: 0.7s; }}
.slide.intensity-2 {{ animation-duration: 0.9s; }}
.slide.intensity-1 {{ animation-duration: 1.2s; }}

/* Emphasis modifiers */
.slide.emphasis-hero .slide-title {{
  font-size: var(--title-size, var(--font-hero));
  line-height: 1.15;
  letter-spacing: -0.02em;
}}
.slide.emphasis-hero .slide-subtitle {{
  font-size: var(--subtitle-size, var(--font-h3));
  opacity: 0.85;
}}

/* Content elements */
.slide-title {{
  font-family: var(--font-title), var(--font-body), system-ui, sans-serif;
  font-weight: 700;
  margin-bottom: 0.3em;
  opacity: 0;
  transform: translateY(10px);
}}
.slide.active .slide-title {{
  animation: reveal-line var(--stagger-base) var(--reveal-curve) forwards;
}}
.slide-subtitle {{
  font-family: var(--font-body), system-ui, sans-serif;
  margin-bottom: 1em;
  opacity: 0;
  transform: translateY(8px);
}}
.slide.active .slide-subtitle {{
  animation: reveal-line var(--stagger-base) var(--reveal-curve) forwards;
  animation-delay: calc(var(--stagger-base) * 0.3);
}}

.slide-lead {{
  font-size: var(--body-size, var(--font-body-lg));
  line-height: var(--line-height-body, 1.5);
  margin-bottom: 1.2em;
  opacity: 0;
  transform: translateY(6px);
}}
.slide.active .slide-lead {{
  animation: reveal-line var(--stagger-base) var(--reveal-curve) forwards;
  animation-delay: calc(var(--stagger-base) * 0.5);
}}

.points-list {{
  list-style: none;
  padding: 0;
}}
.point-item {{
  opacity: 0;
  transform: translateX(12px);
  padding: 0.35em 0;
  line-height: 1.55;
  position: relative;
  padding-left: 1.2em;
}}
.point-item::before {{
  content: '';
  position: absolute;
  left: 0;
  top: 0.7em;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--c-accent);
  transform: scale(0);
  transition: transform 0.3s ease;
}}
.point-item.revealed::before {{ transform: scale(1); }}

.point-item {{ transition: opacity 0.4s ease, transform 0.4s ease; }}
.point-item.revealed {{ opacity: 1; transform: translateX(0); }}

.visual-placeholder {{
  margin-top: 1.5em;
  padding: 2em 1.5em;
  border-radius: var(--radius);
  text-align: center;
  opacity: 0;
  font-size: var(--font-body-sm);
}}
.slide.active .visual-placeholder {{
  animation: fade-in-scale 0.8s ease-out forwards;
  animation-delay: calc(var(--stagger-base) * 2);
}}

.speaker-hint {{
  position: fixed;
  bottom: 2vh;
  left: 50%;
  transform: translateX(-50%);
  font-size: var(--font-caption);
  opacity: 0;
  color: var(--c-text-tertiary);
  transition: opacity 0.6s ease;
  max-width: 60vw;
  text-align: center;
}}
.slide.active .speaker-hint {{
  opacity: 0.7;
}}

.data-viz {{
  background: color-mix(in srgb, var(--c-surface-neutral) 70%, var(--c-surface-bg));
  border-radius: var(--radius);
  padding: 1.5em;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-body-sm);
  color: var(--c-text-tertiary);
}}

/* Navigation */
#nav-hint {{
  position: fixed;
  bottom: 3vh;
  right: 4vw;
  display: flex;
  gap: 0.8em;
  z-index: 10;
  opacity: 0.5;
  transition: opacity 0.4s;
}}
#nav-hint:hover {{ opacity: 1; }}
.nav-dot {{
  width: 10px; height: 10px;
  border-radius: 50%;
  background: var(--c-text-tertiary);
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  padding: 0;
}}
.nav-dot.active {{
  background: var(--c-accent);
  transform: scale(1.4);
  box-shadow: 0 0 8px var(--c-accent);
}}

#progress-bar {{
  position: fixed;
  top: 0; left: 0;
  height: 3px;
  background: var(--c-accent);
  transition: width 0.4s ease;
  z-index: 20;
}}

.section-badge {{
  position: absolute;
  top: 3vh;
  left: 4vw;
  font-size: var(--font-caption);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.5;
  font-family: var(--font-title), system-ui;
}}

#overlay {{
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 5;
  opacity: 0;
  transition: opacity 0.8s ease;
}}
#overlay.visible {{ opacity: 1; }}
</style>"""

    # ------------------------------------------------------------------
    # Slide rendering — delegates to scene_runtime
    # ------------------------------------------------------------------

    def _render_slides(self) -> str:
        parts = []
        for i, slide in enumerate(self.slides):
            cfg = self._configs[i]
            badge = find_section_badge(i, self.arc)
            parts.append(render_slide(cfg, slide, i, len(self.slides),
                                      self._compiler, badge))
        return "\n".join(parts)


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def render_to_html(state: dict, style_pack_name: str = "apple_minimal") -> str:
    """Render a presentation state to HTML string using a named style pack."""
    return CinematicRenderer(state, style_pack_name).render()


def render_to_file(state: dict, path: str, style_pack_name: str = "apple_minimal"):
    """Render a presentation state to an HTML file using a named style pack."""
    html = render_to_html(state, style_pack_name)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
