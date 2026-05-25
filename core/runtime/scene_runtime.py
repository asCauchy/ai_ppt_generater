"""Scene Runtime — renders slides using resolved visual configs.

This is a PURE interpretation runtime. It receives ResolvedVisualConfig
objects from the style_resolver and generates HTML. It makes ZERO
aesthetic decisions — it simply translates config fields into DOM elements.

The renderer uses this to build slide HTML without knowing anything
about colors, fonts, spacing, or motion.
"""

from __future__ import annotations

import html as html_mod
from typing import Optional


def render_slide(
    cfg,                # ResolvedVisualConfig
    slide: dict,
    index: int,
    total: int,
    compiler,           # StyleCompiler
    section_badge: str = "",
) -> str:
    """Render a single slide to HTML using only resolved visual config.

    All aesthetic values come from cfg (ResolvedVisualConfig).
    This function owns zero style knowledge.
    """
    content = slide.get("content", {}) or {}
    title = html_mod.escape(slide.get("title", "") or "")
    subtitle = html_mod.escape((slide.get("subtitle") or ""))
    lead = html_mod.escape((content.get("lead") or ""))
    points = _trim_points(slide, cfg)
    visual_desc = content.get("visual_description", "")
    speaker_notes = ((slide.get("notes") or {}).get("speaker_notes", "") or "")
    data = content.get("data")

    # Classes and data attributes
    classes = compiler.compile_slide_classes(cfg)
    data_attrs = compiler.compile_slide_data_attrs(cfg, index)
    inline_css = compiler.compile_slide_inline_css(cfg)

    # Points HTML
    points_html = ""
    if points:
        items = []
        for pi, pt in enumerate(points):
            items.append(
                f'<li class="point-item entrance-{cfg.entrance_type}" '
                f'style="--item-index:{pi}">{html_mod.escape(pt)}</li>'
            )
        points_html = f'<ul class="points-list">{"".join(items)}</ul>'

    # Data viz
    data_html = ""
    if data:
        data_html = (
            f'<div class="data-viz">'
            f'{html_mod.escape(str(data.get("headline", data.get("type", "data"))))}'
            f'</div>'
        )

    # Visual description
    visual_html = ""
    if visual_desc:
        visual_html = (
            f'<div class="visual-placeholder" '
            f'style="background:rgba(255,255,255,0.04);'
            f'border:1px solid rgba(255,255,255,0.08);border-radius:12px;">'
            f'{html_mod.escape(visual_desc)}</div>'
        )

    # Content layout
    content_layout = _build_content_layout(cfg, lead, points_html, data_html, visual_html)

    # Section badge
    badge_html = ""
    if section_badge:
        badge_html = (
            f'<div class="section-badge" style="color: {cfg.text_secondary_color}">'
            f'{html_mod.escape(section_badge)}</div>'
        )

    # Speaker notes
    notes_html = ""
    if speaker_notes:
        notes_html = (
            f'<div class="speaker-hint" style="color: {cfg.text_secondary_color}">'
            f'{html_mod.escape(speaker_notes)}</div>'
        )

    return f"""<section class="{' '.join(classes)}" {data_attrs} style="{inline_css}">
  {cfg.ambient_html}
  {badge_html}
  <div class="slide-inner">
    <h1 class="slide-title">{title}</h1>
    {f'<p class="slide-subtitle">{subtitle}</p>' if subtitle else ''}
    <div class="content-area">
      {content_layout}
    </div>
  </div>
  {notes_html}
</section>"""


def render_overlay() -> str:
    return '<div id="overlay"></div>'


def render_progress(current_pct: float) -> str:
    return f'<div id="progress-bar" style="width: {current_pct}%"></div>'


def render_nav(total: int) -> str:
    dots = []
    for i in range(total):
        active = " active" if i == 0 else ""
        dots.append(
            f'<button class="nav-dot{active}" data-goto="{i}" aria-label="Slide {i + 1}"></button>'
        )
    return f'<nav id="nav-hint">{"".join(dots)}</nav>'


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _trim_points(slide: dict, cfg) -> list[str]:
    """Trim slide points to density limits from config."""
    points = (slide.get("content") or {}).get("points", []) or []
    max_points = cfg.max_points
    max_chars = cfg.max_chars_per_point
    word_limit = cfg.word_limit

    trimmed = []
    for pt in points[:max_points]:
        trimmed.append(pt[:max_chars])

    # For sparse slides (word_limit < 20), keep max 2 points
    if word_limit < 20:
        trimmed = trimmed[:2]

    return trimmed


def _build_content_layout(cfg, lead: str, points_html: str,
                           data_html: str, visual_html: str) -> str:
    """Build content HTML based on resolved layout config."""
    if cfg.is_split_layout:
        left = (
            f'<div class="content-stack">'
            f'{f"<p class=\"slide-lead\">{lead}</p>" if lead else ""}'
            f'{points_html}{visual_html}'
            f'</div>'
        )
        right = f'<div class="content-stack">{data_html}</div>'
        asym_class = " asymmetric" if cfg.asymmetry == "unbalanced" else ""
        return f'<div class="content-split{asym_class}">{left}{right}</div>'
    else:
        lead_html = f'<p class="slide-lead">{lead}</p>' if lead else ""
        return f'{lead_html}{points_html}{data_html}{visual_html}'


def find_section_badge(index: int, narrative_arc: dict) -> str:
    """Find the section label for a slide index."""
    if not narrative_arc:
        return ""
    for sec in narrative_arc.get("sections", []):
        sr = sec.get("slide_range", [])
        if len(sr) == 2 and sr[0] <= index <= sr[1]:
            return sec.get("label", "")
    return ""
