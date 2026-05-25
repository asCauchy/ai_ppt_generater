"""Typography Engine — Phase P4.

Cinematic typography system driven by narrative_role, emotional_role,
rhythm, and emphasis_level. Not a font-size picker — a typographic
composition system.

Principles:
  - Hierarchy over decoration
  - Whitespace over density
  - Restraint over variety
  - Kinetic emphasis over static weight
"""

from __future__ import annotations
from typing import Optional


# ---------------------------------------------------------------------------
# Typographic Scale — musical proportions (1.2 major third)
# ---------------------------------------------------------------------------

TYPE_SCALE = {
    "micro":    10,   # captions, metadata
    "caption":  12,   # labels, hints
    "body-sm":  14,   # secondary body
    "body":     16,   # primary body
    "body-lg":  18,   # lead text
    "h3":       22,   # sub-headings
    "h2":       28,   # section headings
    "h1":       36,   # primary headings
    "hero":     48,   # hero headings
    "display":  64,   # display type
    "mega":     84,   # maximum impact
}

# ---------------------------------------------------------------------------
# Narrative Role → Typography Prescription
# ---------------------------------------------------------------------------

ROLE_TYPOGRAPHY = {
    "hook": {
        "title_scale": "display",
        "title_weight": 800,
        "title_tracking": -0.02,   # tight for impact
        "subtitle_scale": "h3",
        "subtitle_weight": 400,
        "body_scale": "body-lg",
        "body_weight": 400,
        "max_width_ch": 45,        # narrow column for power
        "line_height_title": 1.05,
        "line_height_body": 1.4,
        "word_limit": 12,
        "vertical_align": "center",
        "whitespace_ratio": 0.5,   # 50% whitespace
    },
    "context": {
        "title_scale": "h1",
        "title_weight": 600,
        "title_tracking": -0.01,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 400,
        "body_scale": "body",
        "body_weight": 400,
        "max_width_ch": 60,
        "line_height_title": 1.15,
        "line_height_body": 1.45,
        "word_limit": 30,
        "vertical_align": "top",
        "whitespace_ratio": 0.25,
    },
    "evidence": {
        "title_scale": "h2",
        "title_weight": 600,
        "title_tracking": -0.01,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 400,
        "body_scale": "body",
        "body_weight": 400,
        "max_width_ch": 55,
        "line_height_title": 1.15,
        "line_height_body": 1.5,
        "word_limit": 50,
        "vertical_align": "top",
        "whitespace_ratio": 0.20,
    },
    "insight": {
        "title_scale": "h1",
        "title_weight": 700,
        "title_tracking": -0.015,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 400,
        "body_scale": "body-lg",
        "body_weight": 400,
        "max_width_ch": 50,
        "line_height_title": 1.1,
        "line_height_body": 1.45,
        "word_limit": 35,
        "vertical_align": "center",
        "whitespace_ratio": 0.35,
    },
    "conflict": {
        "title_scale": "h1",
        "title_weight": 700,
        "title_tracking": -0.01,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 500,
        "body_scale": "body",
        "body_weight": 450,
        "max_width_ch": 52,
        "line_height_title": 1.1,
        "line_height_body": 1.35,   # tighter for tension
        "word_limit": 60,
        "vertical_align": "top",
        "whitespace_ratio": 0.15,
    },
    "escalation": {
        "title_scale": "h1",
        "title_weight": 700,
        "title_tracking": -0.01,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 500,
        "body_scale": "body-lg",
        "body_weight": 500,
        "max_width_ch": 48,
        "line_height_title": 1.05,
        "line_height_body": 1.3,    # tighter = more pressure
        "word_limit": 45,
        "vertical_align": "top",
        "whitespace_ratio": 0.12,
    },
    "release": {
        "title_scale": "h1",
        "title_weight": 600,
        "title_tracking": -0.005,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 400,
        "body_scale": "body",
        "body_weight": 400,
        "max_width_ch": 55,
        "line_height_title": 1.15,
        "line_height_body": 1.5,
        "word_limit": 40,
        "vertical_align": "center",
        "whitespace_ratio": 0.35,
    },
    "vision": {
        "title_scale": "hero",
        "title_weight": 700,
        "title_tracking": -0.015,
        "subtitle_scale": "h3",
        "subtitle_weight": 400,
        "body_scale": "body-lg",
        "body_weight": 400,
        "max_width_ch": 48,
        "line_height_title": 1.08,
        "line_height_body": 1.5,
        "word_limit": 20,
        "vertical_align": "center",
        "whitespace_ratio": 0.45,
    },
    "recap": {
        "title_scale": "h2",
        "title_weight": 600,
        "title_tracking": -0.01,
        "subtitle_scale": "body-lg",
        "subtitle_weight": 400,
        "body_scale": "body",
        "body_weight": 400,
        "max_width_ch": 55,
        "line_height_title": 1.15,
        "line_height_body": 1.5,
        "word_limit": 40,
        "vertical_align": "top",
        "whitespace_ratio": 0.25,
    },
    "call_to_action": {
        "title_scale": "hero",
        "title_weight": 800,
        "title_tracking": -0.02,
        "subtitle_scale": "h3",
        "subtitle_weight": 400,
        "body_scale": "body-lg",
        "body_weight": 500,
        "max_width_ch": 40,
        "line_height_title": 1.05,
        "line_height_body": 1.4,
        "word_limit": 12,
        "vertical_align": "center",
        "whitespace_ratio": 0.5,
    },
    "breathing_page": {
        "title_scale": "h2",
        "title_weight": 400,
        "title_tracking": 0.0,
        "subtitle_scale": "body",
        "subtitle_weight": 300,
        "body_scale": "body-sm",
        "body_weight": 300,
        "max_width_ch": 45,
        "line_height_title": 1.3,
        "line_height_body": 1.6,
        "word_limit": 15,
        "vertical_align": "center",
        "whitespace_ratio": 0.6,
    },
}


# ---------------------------------------------------------------------------
# Emotional Role → Kinetic Typography
# ---------------------------------------------------------------------------

KINETIC_TYPOGRAPHY = {
    "curious":     {"emphasis_delay": 0.6, "emphasis_easing": "cubic-bezier(0.2,0,0,1)", "weight_keywords": True},
    "surprised":   {"emphasis_delay": 0.15, "emphasis_easing": "cubic-bezier(0.3,0,1,1)", "weight_keywords": True},
    "reflective":  {"emphasis_delay": 0.9, "emphasis_easing": "cubic-bezier(0.4,0,0.2,1)", "weight_keywords": False},
    "confident":   {"emphasis_delay": 0.3, "emphasis_easing": "cubic-bezier(0,0,0.2,1)", "weight_keywords": True},
    "concerned":   {"emphasis_delay": 0.2, "emphasis_easing": "cubic-bezier(0.4,0,1,1)", "weight_keywords": True},
    "inspired":    {"emphasis_delay": 0.4, "emphasis_easing": "cubic-bezier(0,0.5,0,1)", "weight_keywords": True},
    "determined":  {"emphasis_delay": 0.2, "emphasis_easing": "cubic-bezier(0,0,0.2,1)", "weight_keywords": True},
    "engaged":     {"emphasis_delay": 0.4, "emphasis_easing": "cubic-bezier(0.2,0,0,1)", "weight_keywords": False},
    "excited":     {"emphasis_delay": 0.1, "emphasis_easing": "cubic-bezier(0,0.7,0.3,1)", "weight_keywords": True},
    "hopeful":     {"emphasis_delay": 0.5, "emphasis_easing": "cubic-bezier(0.2,0,0,1)", "weight_keywords": False},
    "skeptical":   {"emphasis_delay": 0.5, "emphasis_easing": "cubic-bezier(0.4,0,0.2,1)", "weight_keywords": False},
    "impressed":   {"emphasis_delay": 0.3, "emphasis_easing": "cubic-bezier(0,0.5,0,1)", "weight_keywords": True},
    "focused":     {"emphasis_delay": 0.3, "emphasis_easing": "cubic-bezier(0.2,0,0,1)", "weight_keywords": False},
    "relieved":    {"emphasis_delay": 0.7, "emphasis_easing": "cubic-bezier(0.4,0,0.2,1)", "weight_keywords": False},
    "motivated":   {"emphasis_delay": 0.25, "emphasis_easing": "cubic-bezier(0,0,0.2,1)", "weight_keywords": True},
    "shocked":     {"emphasis_delay": 0.1, "emphasis_easing": "cubic-bezier(0.3,0,1,1)", "weight_keywords": True},
    "solemn":      {"emphasis_delay": 1.0, "emphasis_easing": "cubic-bezier(0.4,0,0.2,1)", "weight_keywords": False},
    "convinced":   {"emphasis_delay": 0.35, "emphasis_easing": "cubic-bezier(0,0,0.2,1)", "weight_keywords": False},
}


# ---------------------------------------------------------------------------
# Intensity → Content Density Prescription
# ---------------------------------------------------------------------------

INTENSITY_DENSITY = {
    1: {"max_points": 2, "max_chars_per_point": 40, "max_points_total": 50},
    2: {"max_points": 3, "max_chars_per_point": 60, "max_points_total": 120},
    3: {"max_points": 4, "max_chars_per_point": 80, "max_points_total": 200},
    4: {"max_points": 5, "max_chars_per_point": 90, "max_points_total": 300},
    5: {"max_points": 7, "max_chars_per_point": 100, "max_points_total": 400},
}

# ---------------------------------------------------------------------------
# Spacing scale — vertical rhythm
# ---------------------------------------------------------------------------

SPACING = {
    "micro":  4,
    "xs":     8,
    "sm":     12,
    "md":     20,
    "lg":     32,
    "xl":     48,
    "2xl":    64,
    "3xl":    96,
    "4xl":    144,
}


class TypographyEngine:
    """State-driven typography system.

    Usage:
        engine = TypographyEngine()
        spec = engine.get_spec(slide)  # returns typography prescription
    """

    def get_spec(self, slide: dict) -> dict:
        """Get typography prescription for a slide."""
        n_role = slide.get("narrative_role", "")
        e_role = slide.get("emotional_role", "")
        rhythm = slide.get("rhythm", {}) or {}
        emphasis = (slide.get("design") or {}).get("emphasis_level", "normal")
        intensity = rhythm.get("intensity", 3)

        role_spec = ROLE_TYPOGRAPHY.get(n_role, ROLE_TYPOGRAPHY["context"]).copy()
        kinetic = KINETIC_TYPOGRAPHY.get(e_role, {})

        # Scale title up for hero emphasis
        if emphasis == "hero":
            current = role_spec["title_scale"]
            scale_up = {"hero": "display", "display": "mega", "h1": "hero", "h2": "h1", "h3": "h2"}
            role_spec["title_scale"] = scale_up.get(current, current)

        # Intensity modifies body scale
        body_map = {1: "body-sm", 2: "body-sm", 3: "body", 4: "body-lg", 5: "body-lg"}
        role_spec["body_scale"] = body_map.get(intensity, "body")

        role_spec["kinetic"] = kinetic
        role_spec["intensity"] = intensity
        role_spec["density"] = INTENSITY_DENSITY.get(intensity, INTENSITY_DENSITY[3])

        return role_spec

    def css_for_slide(self, slide: dict) -> str:
        """Generate inline CSS custom properties for a slide's typography."""
        spec = self.get_spec(slide)
        title_size = TYPE_SCALE.get(spec["title_scale"], 36)
        subtitle_size = TYPE_SCALE.get(spec.get("subtitle_scale", "body-lg"), 18)
        body_size = TYPE_SCALE.get(spec.get("body_scale", "body"), 16)

        return f"""--title-size: {title_size}px;
--title-weight: {spec['title_weight']};
--title-tracking: {spec['title_tracking']}em;
--subtitle-size: {subtitle_size}px;
--subtitle-weight: {spec.get('subtitle_weight', 400)};
--body-size: {body_size}px;
--body-weight: {spec.get('body_weight', 400)};
--line-height-title: {spec['line_height_title']};
--line-height-body: {spec['line_height_body']};
--max-width-ch: {spec['max_width_ch']}ch;
--whitespace-ratio: {spec['whitespace_ratio']};
--vertical-align: {spec['vertical_align']};"""

    def trim_points(self, slide: dict) -> list[str]:
        """Apply content density limits to slide points."""
        spec = self.get_spec(slide)
        density = spec["density"]
        points = (slide.get("content") or {}).get("points", []) or []

        # Apply word limit filter
        max_points = density["max_points"]
        max_chars = density["max_chars_per_point"]
        max_total = density["max_points_total"]

        trimmed = []
        total_chars = 0
        for pt in points[:max_points]:
            if total_chars >= max_total:
                break
            trimmed_pt = pt[:max_chars]
            trimmed.append(trimmed_pt)
            total_chars += len(trimmed_pt)

        return trimmed
