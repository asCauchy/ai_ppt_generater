"""Style System Schema — P5 Style Runtime Abstraction Layer.

Defines every data structure in the style operating system:
  - StylePack: the complete replaceable aesthetic unit
  - SemanticRequirements: what the state needs (style-agnostic)
  - ResolvedVisualConfig: what the renderer consumes (style-resolved)

No rendering logic. No CSS. Pure data contracts.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# Color System
# ============================================================================

@dataclass
class ColorSystem:
    """Complete semantic color palette. Every color has a semantic role."""
    # Primary brand
    primary: str = "#003D6B"
    primary_light: str = "#5B9BD5"
    primary_dark: str = "#002440"

    # Accent
    accent: str = "#E8A838"
    accent_light: str = "#F5D78C"
    accent_dark: str = "#B8861E"

    # Surfaces
    surface_bg: str = "#FFFFFF"
    surface_neutral: str = "#F0F2F5"
    surface_dark: str = "#0A1628"
    surface_mid: str = "#1A2744"
    surface_glass: str = "rgba(255,255,255,0.08)"
    surface_raised: str = "#F8F9FA"
    surface_sunken: str = "#E8ECF0"

    # Text
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#666666"
    text_tertiary: str = "#999999"
    text_on_dark: str = "#E8ECF0"
    text_on_dark_secondary: str = "rgba(200,210,225,0.7)"
    text_on_brand: str = "#FFFFFF"
    text_on_brand_secondary: str = "rgba(255,255,255,0.75)"

    # Semantic
    success: str = "#22C55E"
    warning: str = "#F59E0B"
    danger: str = "#EF4444"
    info: str = "#3B82F6"

    # Cinematic
    glow: str = "rgba(232,168,56,0.15)"
    shadow: str = "rgba(0,0,0,0.06)"
    overlay_dark: str = "rgba(0,0,0,0.4)"
    overlay_light: str = "rgba(255,255,255,0.1)"


# ============================================================================
# Typography System
# ============================================================================

@dataclass
class TypographySystem:
    """Font families, scale, and role-based prescriptions."""
    # Font stacks
    title_font: str = "system-ui, -apple-system, sans-serif"
    body_font: str = "system-ui, -apple-system, sans-serif"
    mono_font: str = "'SF Mono', 'Fira Code', monospace"

    # Type scale (px) — musical proportions
    scale_micro: int = 10
    scale_caption: int = 12
    scale_body_sm: int = 14
    scale_body: int = 16
    scale_body_lg: int = 18
    scale_h3: int = 22
    scale_h2: int = 28
    scale_h1: int = 36
    scale_hero: int = 48
    scale_display: int = 64
    scale_mega: int = 84

    # Role prescriptions — narrative_role → type spec
    # Each role maps to: {title_scale, title_weight, title_tracking,
    #                     subtitle_scale, body_scale, max_width_ch,
    #                     line_height_title, line_height_body,
    #                     word_limit, vertical_align, whitespace_ratio}
    role_prescriptions: dict = field(default_factory=lambda: {
        "hook": {
            "title_scale": "display", "title_weight": 800, "title_tracking": -0.02,
            "subtitle_scale": "h3", "subtitle_weight": 400,
            "body_scale": "body_lg", "body_weight": 400,
            "max_width_ch": 45, "line_height_title": 1.05, "line_height_body": 1.4,
            "word_limit": 12, "vertical_align": "center", "whitespace_ratio": 0.5,
        },
        "context": {
            "title_scale": "h1", "title_weight": 600, "title_tracking": -0.01,
            "subtitle_scale": "body_lg", "subtitle_weight": 400,
            "body_scale": "body", "body_weight": 400,
            "max_width_ch": 60, "line_height_title": 1.15, "line_height_body": 1.45,
            "word_limit": 30, "vertical_align": "top", "whitespace_ratio": 0.25,
        },
        "evidence": {
            "title_scale": "h2", "title_weight": 600, "title_tracking": -0.01,
            "subtitle_scale": "body_lg", "subtitle_weight": 400,
            "body_scale": "body", "body_weight": 400,
            "max_width_ch": 55, "line_height_title": 1.15, "line_height_body": 1.5,
            "word_limit": 50, "vertical_align": "top", "whitespace_ratio": 0.20,
        },
        "insight": {
            "title_scale": "h1", "title_weight": 700, "title_tracking": -0.015,
            "subtitle_scale": "body_lg", "subtitle_weight": 400,
            "body_scale": "body_lg", "body_weight": 400,
            "max_width_ch": 50, "line_height_title": 1.1, "line_height_body": 1.45,
            "word_limit": 35, "vertical_align": "center", "whitespace_ratio": 0.35,
        },
        "conflict": {
            "title_scale": "h1", "title_weight": 700, "title_tracking": -0.01,
            "subtitle_scale": "body_lg", "subtitle_weight": 500,
            "body_scale": "body", "body_weight": 450,
            "max_width_ch": 52, "line_height_title": 1.1, "line_height_body": 1.35,
            "word_limit": 60, "vertical_align": "top", "whitespace_ratio": 0.15,
        },
        "escalation": {
            "title_scale": "h1", "title_weight": 700, "title_tracking": -0.01,
            "subtitle_scale": "body_lg", "subtitle_weight": 500,
            "body_scale": "body_lg", "body_weight": 500,
            "max_width_ch": 48, "line_height_title": 1.05, "line_height_body": 1.3,
            "word_limit": 45, "vertical_align": "top", "whitespace_ratio": 0.12,
        },
        "release": {
            "title_scale": "h1", "title_weight": 600, "title_tracking": -0.005,
            "subtitle_scale": "body_lg", "subtitle_weight": 400,
            "body_scale": "body", "body_weight": 400,
            "max_width_ch": 55, "line_height_title": 1.15, "line_height_body": 1.5,
            "word_limit": 40, "vertical_align": "center", "whitespace_ratio": 0.35,
        },
        "vision": {
            "title_scale": "hero", "title_weight": 700, "title_tracking": -0.015,
            "subtitle_scale": "h3", "subtitle_weight": 400,
            "body_scale": "body_lg", "body_weight": 400,
            "max_width_ch": 48, "line_height_title": 1.08, "line_height_body": 1.5,
            "word_limit": 20, "vertical_align": "center", "whitespace_ratio": 0.45,
        },
        "recap": {
            "title_scale": "h2", "title_weight": 600, "title_tracking": -0.01,
            "subtitle_scale": "body_lg", "subtitle_weight": 400,
            "body_scale": "body", "body_weight": 400,
            "max_width_ch": 55, "line_height_title": 1.15, "line_height_body": 1.5,
            "word_limit": 40, "vertical_align": "top", "whitespace_ratio": 0.25,
        },
        "call_to_action": {
            "title_scale": "hero", "title_weight": 800, "title_tracking": -0.02,
            "subtitle_scale": "h3", "subtitle_weight": 400,
            "body_scale": "body_lg", "body_weight": 500,
            "max_width_ch": 40, "line_height_title": 1.05, "line_height_body": 1.4,
            "word_limit": 12, "vertical_align": "center", "whitespace_ratio": 0.5,
        },
        "breathing_page": {
            "title_scale": "h2", "title_weight": 400, "title_tracking": 0.0,
            "subtitle_scale": "body", "subtitle_weight": 300,
            "body_scale": "body_sm", "body_weight": 300,
            "max_width_ch": 45, "line_height_title": 1.3, "line_height_body": 1.6,
            "word_limit": 15, "vertical_align": "center", "whitespace_ratio": 0.6,
        },
    })


# ============================================================================
# Composition System
# ============================================================================

@dataclass
class CompositionSystem:
    """Spatial composition rules — scene weight, focal points, negative space."""
    scene_weight: dict = field(default_factory=lambda: {
        "hook": "medium", "context": "light", "evidence": "medium_heavy",
        "insight": "heavy", "conflict": "maximum", "escalation": "maximum",
        "release": "medium_light", "vision": "medium_heavy",
        "recap": "light", "call_to_action": "heavy", "breathing_page": "minimal",
    })

    focal_points: dict = field(default_factory=lambda: {
        "hook": {"primary": "center", "gaze_path": "direct", "hierarchy_gap": "large"},
        "context": {"primary": "top_left", "gaze_path": "z_pattern", "hierarchy_gap": "medium"},
        "evidence": {"primary": "left", "gaze_path": "left_to_right", "hierarchy_gap": "small"},
        "insight": {"primary": "center_left", "gaze_path": "diagonal", "hierarchy_gap": "large"},
        "conflict": {"primary": "top", "gaze_path": "fragmented", "hierarchy_gap": "tight"},
        "escalation": {"primary": "top", "gaze_path": "vertical_pressure", "hierarchy_gap": "tight"},
        "release": {"primary": "center", "gaze_path": "stable", "hierarchy_gap": "large"},
        "vision": {"primary": "center", "gaze_path": "expanding", "hierarchy_gap": "very_large"},
        "recap": {"primary": "top", "gaze_path": "horizontal_scan", "hierarchy_gap": "medium"},
        "call_to_action": {"primary": "absolute_center", "gaze_path": "direct", "hierarchy_gap": "maximum"},
        "breathing_page": {"primary": "center", "gaze_path": "pause", "hierarchy_gap": "maximum"},
    })

    negative_space: dict = field(default_factory=lambda: {
        "hook": 0.50, "context": 0.25, "evidence": 0.18, "insight": 0.35,
        "conflict": 0.12, "escalation": 0.10, "release": 0.38, "vision": 0.45,
        "recap": 0.28, "call_to_action": 0.55, "breathing_page": 0.65,
    })

    asymmetry: dict = field(default_factory=lambda: {
        "hook": "symmetric", "context": "slight_left", "evidence": "left_weighted",
        "insight": "dynamic_shift", "conflict": "unbalanced", "escalation": "unbalanced",
        "release": "balanced", "vision": "symmetric",
        "recap": "balanced", "call_to_action": "symmetric", "breathing_page": "symmetric",
    })

    depth_layers: dict = field(default_factory=lambda: {
        "hook": ["ambient_glow", "foreground_text", "accent_line"],
        "context": ["ambient_glow", "foreground_text"],
        "evidence": ["ambient_glow", "surface_panel", "foreground_text"],
        "insight": ["ambient_glow", "accent_wash", "foreground_text", "emphasis_marker"],
        "conflict": ["dark_base", "tension_lines", "foreground_text", "pressure_overlay"],
        "escalation": ["dark_base", "rising_gradient", "foreground_text", "intensity_lines"],
        "release": ["light_base", "soft_glow", "foreground_text"],
        "vision": ["horizon_gradient", "glow_sphere", "foreground_text", "accent_dust"],
        "recap": ["light_base", "pillar_structure", "foreground_text"],
        "call_to_action": ["brand_base", "foreground_text", "impact_ring"],
        "breathing_page": ["subtle_gradient", "foreground_text"],
    })

    # Grid templates for each asymmetry type
    grid_templates: dict = field(default_factory=lambda: {
        "symmetric": "1fr min(1100px, 90vw) 1fr",
        "slight_left": "1.15fr 1fr",
        "left_weighted": "1.4fr 1fr",
        "unbalanced": "1.5fr 1fr",
        "balanced": "1fr 1fr",
        "dynamic_shift": "1.3fr 1fr",
        "centered": "1fr",
    })

    container_class: dict = field(default_factory=lambda: {
        "hook": "fullscreen_hero",
        "context": "overview_grid",
        "evidence": "split_content",
        "insight": "reframe_panel",
        "conflict": "tension_split",
        "escalation": "intensify_stack",
        "release": "relief_spread",
        "vision": "horizon_canvas",
        "recap": "pillars_grid",
        "call_to_action": "focal_center",
        "breathing_page": "breathing_space",
    })


# ============================================================================
# Motion Language
# ============================================================================

@dataclass
class MotionLanguage:
    """Motion grammar — easing curves, entrance animations, stagger patterns."""
    # Global easing philosophy
    default_easing: str = "cubic-bezier(0.22, 0, 0, 1)"  # Apple-style
    emphatic_easing: str = "cubic-bezier(0, 0.7, 0.3, 1)"
    gentle_easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    snappy_easing: str = "cubic-bezier(0, 0, 0.2, 1)"
    dramatic_easing: str = "cubic-bezier(0.3, 0, 1, 1)"

    # Emotional role → entrance animation mapping
    emotional_entrance: dict = field(default_factory=lambda: {
        "curious": {"type": "delayed_reveal", "stagger_ms": 200, "easing": "gentle", "scale_var": 0},
        "surprised": {"type": "sudden_appear", "stagger_ms": 80, "easing": "dramatic", "scale_var": 0.05},
        "shocked": {"type": "impact_reveal", "stagger_ms": 60, "easing": "dramatic", "scale_var": 0.08},
        "reflective": {"type": "slow_dissolve", "stagger_ms": 400, "easing": "gentle", "scale_var": 0},
        "confident": {"type": "strong_enter", "stagger_ms": 150, "easing": "snappy", "scale_var": 0.02},
        "concerned": {"type": "tense_reveal", "stagger_ms": 120, "easing": "dramatic", "scale_var": 0.03},
        "skeptical": {"type": "questioning_reveal", "stagger_ms": 180, "easing": "gentle", "scale_var": 0},
        "inspired": {"type": "rising_reveal", "stagger_ms": 150, "easing": "emphatic", "scale_var": 0.04},
        "excited": {"type": "burst_reveal", "stagger_ms": 100, "easing": "emphatic", "scale_var": 0.06},
        "hopeful": {"type": "warm_fade", "stagger_ms": 250, "easing": "gentle", "scale_var": 0.01},
        "determined": {"type": "resolve_enter", "stagger_ms": 100, "easing": "snappy", "scale_var": 0.03},
        "engaged": {"type": "active_reveal", "stagger_ms": 180, "easing": "default", "scale_var": 0.01},
        "convinced": {"type": "solid_build", "stagger_ms": 200, "easing": "snappy", "scale_var": 0},
        "impressed": {"type": "scale_reveal", "stagger_ms": 150, "easing": "emphatic", "scale_var": 0.04},
        "focused": {"type": "sharp_enter", "stagger_ms": 120, "easing": "snappy", "scale_var": 0},
        "relieved": {"type": "gentle_unfold", "stagger_ms": 300, "easing": "gentle", "scale_var": 0},
        "motivated": {"type": "drive_forward", "stagger_ms": 120, "easing": "snappy", "scale_var": 0.02},
        "solemn": {"type": "respectful_fade", "stagger_ms": 500, "easing": "gentle", "scale_var": 0},
    })

    # Intensity → animation speed modifier
    intensity_speed: dict = field(default_factory=lambda: {
        1: {"duration_mult": 1.0, "stagger_mult": 1.5},
        2: {"duration_mult": 0.85, "stagger_mult": 1.25},
        3: {"duration_mult": 0.7, "stagger_mult": 1.0},
        4: {"duration_mult": 0.5, "stagger_mult": 0.7},
        5: {"duration_mult": 0.3, "stagger_mult": 0.5},
    })

    # Keyframe definitions (reusable animation primitives)
    keyframes: dict = field(default_factory=lambda: {
        "reveal_line": "@keyframes reveal-line { to { opacity: 1; transform: translateY(0); } }",
        "reveal_scale": "@keyframes reveal-scale { to { opacity: 1; transform: scale(1); } }",
        "fade_in_scale": "@keyframes fade-in-scale { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }",
        "slide_up": "@keyframes slide-up { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }",
        "pulse_glow": "@keyframes pulse-glow { 0%, 100% { box-shadow: 0 0 8px var(--c-accent); } 50% { box-shadow: 0 0 20px var(--c-accent), 0 0 40px color-mix(in srgb, var(--c-accent) 50%, transparent); } }",
    })


# ============================================================================
# Transition Language
# ============================================================================

@dataclass
class TransitionLanguage:
    """Slide-to-slide transition vocabulary."""
    default_transition: str = "slide_fade"
    default_duration_ms: int = 500
    default_easing: str = "cubic-bezier(0.22, 0, 0, 1)"

    # relation_to_next → transition type
    relation_transitions: dict = field(default_factory=lambda: {
        "progression": {"type": "slide_fade", "duration_ms": 500, "easing": "cubic-bezier(0.22, 0, 0, 1)"},
        "deepening": {"type": "morph_deepen", "duration_ms": 800, "easing": "cubic-bezier(0.4, 0, 0.2, 1)"},
        "contrast": {"type": "hard_cut", "duration_ms": 150, "easing": "step-end"},
        "elaboration": {"type": "expand_detail", "duration_ms": 600, "easing": "cubic-bezier(0.22, 0, 0, 1)"},
        "example": {"type": "zoom_example", "duration_ms": 500, "easing": "cubic-bezier(0, 0.7, 0.3, 1)"},
        "escalation": {"type": "intensify", "duration_ms": 300, "easing": "cubic-bezier(0.3, 0, 1, 1)"},
        "recap": {"type": "compress_return", "duration_ms": 600, "easing": "cubic-bezier(0.22, 0, 0, 1)"},
        "pivot": {"type": "swing_pivot", "duration_ms": 700, "easing": "cubic-bezier(0.6, 0, 0.4, 1)"},
        "echo": {"type": "recall_fade", "duration_ms": 900, "easing": "cubic-bezier(0.4, 0, 0.2, 1)"},
        "emotional_shift": {"type": "color_shift", "duration_ms": 600, "easing": "cubic-bezier(0.4, 0, 0.2, 1)"},
        "build": {"type": "layer_up", "duration_ms": 400, "easing": "cubic-bezier(0.22, 0, 0, 1)"},
        "summary": {"type": "pull_back", "duration_ms": 700, "easing": "cubic-bezier(0.4, 0, 0.2, 1)"},
    })


# ============================================================================
# Surface System
# ============================================================================

@dataclass
class SurfaceSystem:
    """Surface treatments — backgrounds, gradients, overlays per narrative_role."""
    surfaces: dict = field(default_factory=lambda: {
        "hook": {
            "background": "brand_gradient",
            "text_color": "text_on_brand",
            "text_secondary": "text_on_brand_secondary",
            "ambient": "glow",
            "accent_glow": True,
        },
        "context": {
            "background": "surface_bg",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "none",
            "accent_glow": False,
        },
        "evidence": {
            "background": "surface_bg",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "none",
            "accent_glow": False,
        },
        "insight": {
            "background": "accent_wash",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "glow",
            "accent_glow": True,
        },
        "conflict": {
            "background": "tension_gradient",
            "text_color": "text_on_dark",
            "text_secondary": "text_on_dark_secondary",
            "ambient": "none",
            "accent_glow": False,
        },
        "escalation": {
            "background": "dark_gradient",
            "text_color": "text_on_dark",
            "text_secondary": "text_on_dark_secondary",
            "ambient": "none",
            "accent_glow": False,
        },
        "release": {
            "background": "soft_gradient",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "glow",
            "accent_glow": True,
        },
        "vision": {
            "background": "horizon_gradient",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "glow",
            "accent_glow": True,
        },
        "recap": {
            "background": "surface_bg",
            "text_color": "text_primary",
            "text_secondary": "text_tertiary",
            "ambient": "none",
            "accent_glow": False,
        },
        "call_to_action": {
            "background": "brand_solid",
            "text_color": "text_on_brand",
            "text_secondary": "text_on_brand_secondary",
            "ambient": "none",
            "accent_glow": True,
        },
        "breathing_page": {
            "background": "surface_bg",
            "text_color": "text_tertiary",
            "text_secondary": "text_tertiary",
            "ambient": "none",
            "accent_glow": False,
        },
    })

    # Named background CSS generators (use semantic color references)
    background_css: dict = field(default_factory=lambda: {
        "brand_gradient": "linear-gradient(135deg, var(--c-primary) 0%, var(--c-primary-light) 100%)",
        "brand_solid": "var(--c-primary)",
        "dark_gradient": "linear-gradient(170deg, var(--c-surface-dark) 0%, var(--c-surface-mid) 40%, var(--c-primary-dark) 100%)",
        "tension_gradient": "linear-gradient(160deg, var(--c-surface-dark) 0%, var(--c-surface-mid) 50%, var(--c-primary-dark) 100%)",
        "horizon_gradient": "linear-gradient(180deg, var(--c-surface-bg) 0%, color-mix(in srgb, var(--c-accent) 8%, var(--c-surface-bg)) 50%, color-mix(in srgb, var(--c-primary) 5%, var(--c-surface-bg)) 100%)",
        "soft_gradient": "linear-gradient(180deg, var(--c-surface-bg) 0%, var(--c-surface-neutral) 100%)",
        "accent_wash": "linear-gradient(135deg, var(--c-surface-bg) 0%, color-mix(in srgb, var(--c-accent) 12%, var(--c-surface-bg)) 100%)",
        "surface_bg": "var(--c-surface-bg)",
        "surface_neutral": "var(--c-surface-neutral)",
        "subtle_gradient": "color-mix(in srgb, var(--c-surface-neutral) 50%, var(--c-surface-bg))",
    })

    # Ambient CSS classes that style packs can customize
    ambient_css_template: str = """
/* Glass surface */
.surface-glass {
  background: {glass};
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
}
/* Noise texture overlay */
.noise-overlay::after {
  content: '';
  position: absolute; inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events: none;
}
/* Ambient glow sphere */
.glow-sphere {
  position: absolute; border-radius: 50%; filter: blur(120px);
  pointer-events: none; z-index: 0;
}
.glow-sphere.top-right { top: -20%; right: -15%; width: 50vw; height: 50vw; max-width: 600px; max-height: 600px; background: var(--c-glow); opacity: 0.4; }
.glow-sphere.center { top: 50%; left: 50%; transform: translate(-50%, -50%); width: 50vw; height: 50vw; max-width: 600px; max-height: 600px; background: var(--c-glow); opacity: 0.25; }
.glow-sphere.bottom { bottom: -25%; left: 30%; width: 50vw; height: 50vw; max-width: 600px; max-height: 600px; background: var(--c-glow); opacity: 0.35; }
/* Accent line */
.accent-line { position: absolute; background: linear-gradient(90deg, var(--c-accent), transparent); height: 1px; width: 30%; opacity: 0.3; }
.accent-line.top { top: 8vh; left: 6vw; }
.accent-line.bottom { bottom: 8vh; right: 6vw; transform: scaleX(-1); }
/* Tension lines */
.tension-lines { position: absolute; inset: 0; pointer-events: none; z-index: 0; background: linear-gradient(0deg, transparent 0%, rgba(255,255,255,0.02) 50%, transparent 100%), repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(255,255,255,0.015) 40px, rgba(255,255,255,0.015) 41px); }
/* Impact ring */
.impact-ring { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: min(50vw, 500px); height: min(50vw, 500px); border-radius: 50%; border: 1px solid rgba(255,255,255,0.08); pointer-events: none; z-index: 0; }
/* Rising gradient */
.rising-gradient { position: absolute; bottom: 0; left: 0; right: 0; height: 40%; background: linear-gradient(0deg, rgba(255,255,255,0.04) 0%, transparent 100%); pointer-events: none; z-index: 0; }
/* Surface panel */
.surface-panel { background: var(--c-surface-raised); border-radius: 12px; padding: 2em; box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03); }
/* Accent dust */
.accent-dust { position: absolute; pointer-events: none; z-index: 0; width: 100%; height: 100%; top: 0; left: 0; background: radial-gradient(1px 1px at 20% 30%, var(--c-accent), transparent), radial-gradient(1px 1px at 60% 70%, var(--c-accent), transparent), radial-gradient(1px 1px at 80% 20%, var(--c-accent), transparent), radial-gradient(1px 1px at 40% 80%, var(--c-primary-light), transparent), radial-gradient(1px 1px at 70% 50%, var(--c-primary-light), transparent); opacity: 0.2; }
/* Emphasis marker */
.emphasis-marker { position: absolute; left: 4vw; top: 50%; transform: translateY(-50%); width: 2px; height: 30%; background: linear-gradient(180deg, transparent, var(--c-accent), transparent); opacity: 0.3; }
/* Pillar structure */
.pillar-structure { position: absolute; top: 20%; bottom: 20%; width: 100%; pointer-events: none; z-index: 0; display: flex; justify-content: space-around; }
.pillar-structure::before, .pillar-structure::after { content: ''; width: 1px; height: 100%; background: linear-gradient(180deg, transparent, rgba(0,0,0,0.06), transparent); }
/* Pressure overlay */
.pressure-overlay { position: absolute; inset: 0; background: radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.15) 100%); pointer-events: none; z-index: 0; }
/* Intensity lines */
.intensity-lines { position: absolute; inset: 0; pointer-events: none; z-index: 0; background: repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(255,255,255,0.02) 60px, rgba(255,255,255,0.02) 61px); }
"""


# ============================================================================
# Spacing System
# ============================================================================

@dataclass
class SpacingSystem:
    """Spatial rhythm — padding, gaps, margins scale."""
    unit_px: int = 8
    scale: dict = field(default_factory=lambda: {
        "micro": 4, "xs": 8, "sm": 12, "md": 20, "lg": 32,
        "xl": 48, "2xl": 64, "3xl": 96, "4xl": 144,
    })
    slide_padding_v: str = "6vh"
    slide_padding_h: str = "6vw"
    content_gap: str = "0.5em"
    section_gap: str = "2em"
    element_gap: str = "1em"
    title_margin_bottom: str = "0.3em"
    subtitle_margin_bottom: str = "1em"
    point_padding: str = "0.35em 0"
    list_left_pad: str = "1.2em"


# ============================================================================
# Density System
# ============================================================================

@dataclass
class DensitySystem:
    """Content density limits per intensity level."""
    levels: dict = field(default_factory=lambda: {
        1: {"max_points": 2, "max_chars_per_point": 40, "max_total_chars": 50},
        2: {"max_points": 3, "max_chars_per_point": 60, "max_total_chars": 120},
        3: {"max_points": 4, "max_chars_per_point": 80, "max_total_chars": 200},
        4: {"max_points": 5, "max_chars_per_point": 90, "max_total_chars": 300},
        5: {"max_points": 7, "max_chars_per_point": 100, "max_total_chars": 400},
    })


# ============================================================================
# Emphasis System
# ============================================================================

@dataclass
class EmphasisSystem:
    """Visual hierarchy — how emphasis levels modify the presentation."""
    level_modifiers: dict = field(default_factory=lambda: {
        "hero": {
            "title_scale_up": {"hero": "display", "display": "mega", "h1": "hero", "h2": "h1", "h3": "h2"},
            "subtitle_scale_up": True,
            "accent_intensity": "maximum",
        },
        "normal": {
            "title_scale_up": {},
            "subtitle_scale_up": False,
            "accent_intensity": "medium",
        },
        "subtle": {
            "title_scale_up": {"hero": "h1", "display": "hero", "h1": "h2", "h2": "h3"},
            "subtitle_scale_up": False,
            "accent_intensity": "low",
        },
    })


# ============================================================================
# Cinematic Rhythm
# ============================================================================

@dataclass
class CinematicRhythm:
    """Pacing curves and tension profiles across the presentation arc."""
    # How pacing changes across the slide sequence
    act_pacing: dict = field(default_factory=lambda: {
        "opening": {"pace": "slow", "intensity_baseline": 2, "transition_spacing": "generous"},
        "build": {"pace": "moderate", "intensity_baseline": 3, "transition_spacing": "normal"},
        "climax": {"pace": "fast", "intensity_baseline": 5, "transition_spacing": "tight"},
        "release": {"pace": "slow", "intensity_baseline": 2, "transition_spacing": "generous"},
        "closing": {"pace": "moderate", "intensity_baseline": 4, "transition_spacing": "normal"},
    })

    # Global tension curve (where in the presentation each intensity lives)
    tension_curve: list[dict] = field(default_factory=lambda: [
        {"position_pct": 0, "intensity": 3},
        {"position_pct": 15, "intensity": 2},
        {"position_pct": 40, "intensity": 4},
        {"position_pct": 60, "intensity": 5},
        {"position_pct": 75, "intensity": 4},
        {"position_pct": 90, "intensity": 3},
        {"position_pct": 100, "intensity": 5},
    ])


# ============================================================================
# Emotional Mapping
# ============================================================================

@dataclass
class EmotionalMapping:
    """How emotional roles translate to kinetic typography behavior."""
    kinetic_typography: dict = field(default_factory=lambda: {
        "curious": {"emphasis_delay": 0.6, "emphasis_easing": "gentle", "weight_keywords": True},
        "surprised": {"emphasis_delay": 0.15, "emphasis_easing": "dramatic", "weight_keywords": True},
        "shocked": {"emphasis_delay": 0.1, "emphasis_easing": "dramatic", "weight_keywords": True},
        "reflective": {"emphasis_delay": 0.9, "emphasis_easing": "gentle", "weight_keywords": False},
        "confident": {"emphasis_delay": 0.3, "emphasis_easing": "snappy", "weight_keywords": True},
        "concerned": {"emphasis_delay": 0.2, "emphasis_easing": "dramatic", "weight_keywords": True},
        "skeptical": {"emphasis_delay": 0.5, "emphasis_easing": "gentle", "weight_keywords": False},
        "inspired": {"emphasis_delay": 0.4, "emphasis_easing": "emphatic", "weight_keywords": True},
        "excited": {"emphasis_delay": 0.1, "emphasis_easing": "emphatic", "weight_keywords": True},
        "hopeful": {"emphasis_delay": 0.5, "emphasis_easing": "gentle", "weight_keywords": False},
        "determined": {"emphasis_delay": 0.2, "emphasis_easing": "snappy", "weight_keywords": True},
        "engaged": {"emphasis_delay": 0.4, "emphasis_easing": "default", "weight_keywords": False},
        "convinced": {"emphasis_delay": 0.35, "emphasis_easing": "snappy", "weight_keywords": False},
        "impressed": {"emphasis_delay": 0.3, "emphasis_easing": "emphatic", "weight_keywords": True},
        "focused": {"emphasis_delay": 0.3, "emphasis_easing": "default", "weight_keywords": False},
        "relieved": {"emphasis_delay": 0.7, "emphasis_easing": "gentle", "weight_keywords": False},
        "motivated": {"emphasis_delay": 0.25, "emphasis_easing": "snappy", "weight_keywords": True},
        "solemn": {"emphasis_delay": 1.0, "emphasis_easing": "gentle", "weight_keywords": False},
    })


# ============================================================================
# StylePack — the complete replaceable aesthetic unit
# ============================================================================

@dataclass
class StylePack:
    """A complete, replaceable, inheritable style definition.

    A StylePack contains ALL aesthetic decisions for a presentation style.
    Swapping one StylePack for another changes the entire visual language
    without touching any renderer code.
    """
    name: str
    version: str = "1.0"
    description: str = ""

    # Inheritance
    inherits: Optional[str] = None  # name of parent style pack

    # Systems
    color_system: ColorSystem = field(default_factory=ColorSystem)
    typography_system: TypographySystem = field(default_factory=TypographySystem)
    composition_system: CompositionSystem = field(default_factory=CompositionSystem)
    motion_language: MotionLanguage = field(default_factory=MotionLanguage)
    transition_language: TransitionLanguage = field(default_factory=TransitionLanguage)
    surface_system: SurfaceSystem = field(default_factory=SurfaceSystem)
    spacing_system: SpacingSystem = field(default_factory=SpacingSystem)
    density_system: DensitySystem = field(default_factory=DensitySystem)
    emphasis_system: EmphasisSystem = field(default_factory=EmphasisSystem)
    cinematic_rhythm: CinematicRhythm = field(default_factory=CinematicRhythm)
    emotional_mapping: EmotionalMapping = field(default_factory=EmotionalMapping)

    # Metadata
    metadata: dict = field(default_factory=dict)


# ============================================================================
# SemanticRequirements — what the state layer needs (style-agnostic)
# ============================================================================

@dataclass
class SemanticRequirements:
    """The output of state_mapper. Describes WHAT the slide needs visually,
    without any reference to HOW it should be styled.

    This is the contract between runtime core and style system.
    """
    narrative_role: str = ""
    emotional_role: str = ""
    structural_role: str = ""
    intensity: int = 3
    pace: str = "moderate"
    emphasis_level: str = "normal"
    contrast_level: str = "medium"
    mood: str = "neutral"
    relation_to_next: str = ""
    relation_to_prev: str = ""
    is_first: bool = False
    is_last: bool = False
    position_pct: float = 0.0
    act: str = "build"


# ============================================================================
# ResolvedVisualConfig — what the renderer consumes (style-resolved)
# ============================================================================

@dataclass
class ResolvedVisualConfig:
    """The output of style_resolver. A complete, concrete visual prescription
    for a single slide. Every value is a concrete CSS-compatible string or number.

    The renderer takes this and generates HTML/CSS without making ANY
    aesthetic decisions.
    """
    # Colors (all concrete hex/rgba values)
    bg_color: str = ""
    bg_css: str = ""
    text_color: str = ""
    text_secondary_color: str = ""
    accent_color: str = ""

    # Typography (all concrete px/em values)
    title_font: str = ""
    body_font: str = ""
    title_size_px: int = 36
    title_weight: int = 600
    title_tracking_em: float = -0.01
    subtitle_size_px: int = 18
    body_size_px: int = 16
    body_weight: int = 400
    line_height_title: float = 1.15
    line_height_body: float = 1.5
    max_width_ch: int = 55

    # Spacing (all concrete values)
    slide_padding: str = "6vh 6vw"
    content_gap: str = "0.5em"
    title_margin_bottom: str = "0.3em"

    # Motion
    entrance_type: str = "active_reveal"
    stagger_ms: int = 150
    easing_curve: str = "cubic-bezier(0.22, 0, 0, 1)"
    duration_ms: int = 500
    scale_variation: float = 0.0
    emphasis_delay: float = 0.4
    weight_keywords: bool = False

    # Transition
    transition_type: str = "slide_fade"
    transition_duration_ms: int = 500
    transition_easing: str = "cubic-bezier(0.22, 0, 0, 1)"

    # Layout
    container_class: str = "overview_grid"
    grid_template_columns: str = "1fr"
    grid_template_areas: str = '"content"'
    asymmetry: str = "balanced"
    content_layout_mode: str = "centered"
    is_split_layout: bool = False

    # Surface
    ambient_html: str = ""
    ambient_css_class: str = ""
    accent_glow: bool = False

    # Scene metadata
    narrative_role: str = ""
    intensity: int = 3
    pace: str = "moderate"
    emphasis_level: str = "normal"
    word_limit: int = 30

    # Density
    max_points: int = 4
    max_chars_per_point: int = 80

    # Rhythm
    act: str = "build"
    whitespace_ratio: float = 0.25
    vertical_align: str = "top"
