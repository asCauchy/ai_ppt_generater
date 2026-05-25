"""Composition Engine — Phase P4.

Cinematic spatial composition driven by narrative_role and emphasis.
Not a layout engine — a compositional system.

Principles:
  - Asymmetry over centering
  - Focal point over uniform distribution
  - Negative space over filled canvas
  - Depth layering over flat surfaces
  - Scene weight over uniform density
"""

from __future__ import annotations
from typing import Optional


# ---------------------------------------------------------------------------
# Scene weight — how visually heavy each narrative role should feel
# ---------------------------------------------------------------------------

SCENE_WEIGHT = {
    "hook":           "medium",   # intriguing but not overwhelming
    "context":        "light",     # orientation — don't dominate
    "evidence":       "medium-heavy",
    "insight":        "heavy",     # cognitive impact
    "conflict":       "maximum",   # visual pressure
    "escalation":     "maximum",
    "release":        "medium-light",
    "vision":         "medium-heavy",
    "recap":          "light",
    "call_to_action": "heavy",     # final impact
    "breathing_page": "minimal",
}

# ---------------------------------------------------------------------------
# Focal point prescription per role
# ---------------------------------------------------------------------------

FOCAL_POINTS = {
    "hook": {
        "primary": "center",
        "secondary": None,
        "gaze_path": "direct",      # straight to center
        "hierarchy_gap": "large",   # big gap between primary and secondary
    },
    "context": {
        "primary": "top-left",
        "secondary": "spread",
        "gaze_path": "z-pattern",
        "hierarchy_gap": "medium",
    },
    "evidence": {
        "primary": "left",
        "secondary": "right",
        "gaze_path": "left-to-right",
        "hierarchy_gap": "small",   # data should be dense
    },
    "insight": {
        "primary": "center-left",
        "secondary": "bottom",
        "gaze_path": "diagonal",
        "hierarchy_gap": "large",   # big reveal moment
    },
    "conflict": {
        "primary": "top",
        "secondary": "bottom-right",
        "gaze_path": "fragmented",  # uneasy reading pattern
        "hierarchy_gap": "tight",
    },
    "escalation": {
        "primary": "top",
        "secondary": "cascade",
        "gaze_path": "vertical-pressure",
        "hierarchy_gap": "tight",
    },
    "release": {
        "primary": "center",
        "secondary": "balanced-spread",
        "gaze_path": "stable",
        "hierarchy_gap": "large",
    },
    "vision": {
        "primary": "center",
        "secondary": "horizon",
        "gaze_path": "expanding",
        "hierarchy_gap": "very-large",
    },
    "recap": {
        "primary": "top",
        "secondary": "three-column",
        "gaze_path": "horizontal-scan",
        "hierarchy_gap": "medium",
    },
    "call_to_action": {
        "primary": "absolute-center",
        "secondary": None,
        "gaze_path": "direct",
        "hierarchy_gap": "maximum",
    },
    "breathing_page": {
        "primary": "center",
        "secondary": None,
        "gaze_path": "pause",
        "hierarchy_gap": "maximum",
    },
}

# ---------------------------------------------------------------------------
# Negative space prescription — whitespace ratio per role
# ---------------------------------------------------------------------------

NEGATIVE_SPACE = {
    "hook":           0.50,  # 50% empty space
    "context":        0.25,
    "evidence":       0.18,
    "insight":        0.35,
    "conflict":       0.12,  # almost no breathing room — pressure
    "escalation":     0.10,  # maximum density
    "release":        0.38,
    "vision":         0.45,
    "recap":          0.28,
    "call_to_action": 0.55,  # one message, lots of air
    "breathing_page": 0.65,  # mostly empty
}

# ---------------------------------------------------------------------------
# Asymmetry prescription
# ---------------------------------------------------------------------------

ASYMMETRY = {
    "hook":           "symmetric",       # centered for impact
    "context":        "slight-left",     # structured but not rigid
    "evidence":       "left-weighted",   # data left, viz right
    "insight":        "dynamic-shift",   # surprising balance
    "conflict":       "unbalanced",      # creates unease
    "escalation":     "unbalanced",
    "release":        "balanced",        # return to stability
    "vision":         "symmetric",       # centered for expansiveness
    "recap":          "balanced",
    "call_to_action": "symmetric",       # centered for directness
    "breathing_page": "symmetric",
}

# ---------------------------------------------------------------------------
# Layering prescription — depth layers per scene
# ---------------------------------------------------------------------------

LAYERS = {
    "hook":           ["ambient-glow", "foreground-text", "accent-line"],
    "context":        ["ambient-glow", "foreground-text"],
    "evidence":       ["ambient-glow", "surface-panel", "foreground-text"],
    "insight":        ["ambient-glow", "accent-wash", "foreground-text", "emphasis-marker"],
    "conflict":        ["dark-base", "tension-lines", "foreground-text", "pressure-overlay"],
    "escalation":     ["dark-base", "rising-gradient", "foreground-text", "intensity-lines"],
    "release":        ["light-base", "soft-glow", "foreground-text"],
    "vision":         ["horizon-gradient", "glow-sphere", "foreground-text", "accent-dust"],
    "recap":          ["light-base", "pillar-structure", "foreground-text"],
    "call_to_action": ["brand-base", "foreground-text", "impact-ring"],
    "breathing_page": ["subtle-gradient", "foreground-text"],
}


class CompositionEngine:
    """State-driven composition system.

    Usage:
        engine = CompositionEngine()
        comp = engine.get_composition(slide, position, total_slides)
    """

    def get_composition(self, slide: dict, position: int, total: int) -> dict:
        """Get full composition prescription for a slide."""
        n_role = slide.get("narrative_role", "")
        structural = slide.get("structural_role", "")
        emphasis = (slide.get("design") or {}).get("emphasis_level", "normal")
        rhythm = slide.get("rhythm", {}) or {}
        intensity = rhythm.get("intensity", 3)

        weight = SCENE_WEIGHT.get(n_role, "medium")
        focal = FOCAL_POINTS.get(n_role, FOCAL_POINTS["context"]).copy()
        neg_space = NEGATIVE_SPACE.get(n_role, 0.25)
        asymmetry = ASYMMETRY.get(n_role, "balanced")
        layers = LAYERS.get(n_role, ["ambient-glow", "foreground-text"])

        # Position-aware modulations
        is_first = position == 0
        is_last = position == total - 1
        is_climax = intensity >= 5

        if is_first:
            neg_space = max(neg_space, 0.40)
        if is_last:
            neg_space = max(neg_space, 0.45)
        if is_climax:
            neg_space = min(neg_space, 0.15)

        return {
            "weight": weight,
            "focal": focal,
            "negative_space": neg_space,
            "asymmetry": asymmetry,
            "layers": layers,
            "is_first": is_first,
            "is_last": is_last,
            "is_climax": is_climax,
            "position": position,
            "total": total,
        }

    def css_grid_for(self, comp: dict, slide: dict) -> str:
        """Generate CSS grid template for a composition."""
        n_role = slide.get("narrative_role", "")
        asymmetry = comp["asymmetry"]
        neg = comp["negative_space"]
        design = slide.get("design", {}) or {}

        layout_mode = design.get("layout_mode", "centered")

        # Base grid on layout_mode + asymmetry
        if layout_mode == "centered" or asymmetry == "symmetric":
            grid = "1fr min(1100px, 90vw) 1fr"
            areas = '". content ."'
        elif asymmetry == "left-weighted":
            grid = "1.4fr 1fr"
            areas = '"content side"'
        elif asymmetry == "unbalanced":
            grid = "1.5fr 1fr"
            areas = '"content side"'
        elif asymmetry == "balanced":
            grid = "1fr 1fr"
            areas = '"content side"'
        elif asymmetry == "slight-left":
            grid = "1.15fr 1fr"
            areas = '"content side"'
        elif asymmetry == "dynamic-shift":
            # Alternating: odd slides left-heavy, even slides right-heavy
            pos = comp["position"]
            if pos % 2 == 0:
                grid = "1.3fr 1fr"
                areas = '"content side"'
            else:
                grid = "1fr 1.3fr"
                areas = '"side content"'
        else:
            grid = "1fr"
            areas = '"content"'

        return f"""grid-template-columns: {grid};
grid-template-areas: "{areas}";
"""

    def negspace_css(self, comp: dict) -> str:
        """Generate negative space CSS for a composition."""
        neg = comp["negative_space"]
        # Map to padding multiplier
        pad_base = 4  # vh base
        pad_mult = 0.5 + neg * 3  # 0.5 to 3.5 multiplier
        pad_v = min(12, max(2, pad_base * pad_mult))

        return f"""padding: {pad_v:.0f}vh {max(2, 6 - neg * 4):.0f}vw;
min-height: {100 - int(neg * 40)}vh;
"""
