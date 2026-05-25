"""Aesthetic Intelligence Data Models — intermediate representations for the
style extraction pipeline.

Pipeline:
  Reference Distillation → AestheticObservations (extractor)
  AestheticObservations → NormalizedAestheticSemantics (parser)
  NormalizedAestheticSemantics → StylePack JSON (generator)
  StylePack → DimensionScores (scorer)
  StylePack × N → BenchmarkReport (benchmark)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


# ============================================================================
# AestheticObservations — raw extraction from a reference
# ============================================================================

@dataclass
class TypographyObservation:
    """Raw typography observations from a reference."""
    headline_weight: int = 600          # 100-900
    body_weight: int = 400
    scale_contrast: float = 3.0         # headline / body ratio
    hierarchy_depth: int = 3            # how many distinct size levels
    tracking_character: str = "neutral" # tight / neutral / wide
    font_character: str = "sans_geometric"  # sans_geometric / sans_humanist / serif / mono
    title_font_hint: str = ""
    body_font_hint: str = ""
    line_height_ratio: float = 1.4      # body line-height
    alignment_dominant: str = "left"    # left / center / mixed
    max_line_length_ch: int = 60
    notes: str = ""


@dataclass
class ColorObservation:
    """Raw color observations from a reference."""
    palette_mood: str = "neutral"       # neutral / warm / cool / dramatic / soft
    primary_hex: str = "#333333"
    accent_hex: str = "#0066CC"
    background_hex: str = "#FFFFFF"
    surface_hex: str = "#F5F5F5"
    text_primary_hex: str = "#1A1A1A"
    text_secondary_hex: str = "#666666"
    dark_mode: bool = False
    saturation_level: str = "low"       # low / medium / high
    contrast_ratio: float = 4.5         # estimated text/bg contrast
    accent_usage: str = "sparing"       # sparing / moderate / dominant
    gradient_presence: str = "minimal"  # none / minimal / prominent
    notes: str = ""


@dataclass
class SpacingObservation:
    """Raw spacing observations from a reference."""
    whitespace_ratio: float = 0.30      # estimated fraction of empty space
    padding_character: str = "generous" # tight / moderate / generous / luxurious
    grid_rigor: str = "moderate"        # loose / moderate / strict
    element_gap_ratio: float = 1.0      # gap relative to element size
    vertical_rhythm: str = "regular"    # irregular / regular / strict
    density_feel: str = "moderate"      # sparse / moderate / dense / packed
    margin_asymmetry: str = "symmetric" # symmetric / slight_left / unbalanced
    notes: str = ""


@dataclass
class CompositionObservation:
    """Raw composition observations from a reference."""
    focal_strategy: str = "single_center"   # single_center / split / z_pattern / diagonal / fragmented
    asymmetry_level: str = "balanced"       # symmetric / slight / dynamic / unbalanced
    depth_layers: int = 2                   # how many visual depth planes
    foreground_treatment: str = "direct"    # direct / framed / floating / overlapping
    background_treatment: str = "flat"      # flat / gradient / image / textured / atmospheric
    element_count_per_frame: str = "few"    # minimal(1-3) / few(4-6) / moderate(7-10) / many(11+)
    visual_weight_distribution: str = "balanced"  # balanced / top_heavy / left_heavy / center_heavy
    notes: str = ""


@dataclass
class MotionObservation:
    """Raw motion observations from a reference."""
    easing_philosophy: str = "ease_out"      # linear / ease_out / ease_in_out / spring / custom
    speed_range: str = "moderate"            # slow / moderate / fast / mixed
    stagger_character: str = "sequential"    # simultaneous / sequential / wave / staggered / none
    entrance_style: str = "fade_up"          # fade / fade_up / scale / slide / masked_reveal / cut
    transition_style: str = "dissolve"       # hard_cut / dissolve / push / morph / zoom
    duration_feel: str = "moderate"          # snappy / moderate / leisurely / dramatic
    scale_variation_presence: bool = False
    motion_density: str = "sparse"           # none / sparse / moderate / rich
    notes: str = ""


@dataclass
class SurfaceObservation:
    """Raw surface observations from a reference."""
    surface_quality: str = "flat"            # flat / subtle_gradient / glass / textured / atmospheric
    depth_treatment: str = "shadow"          # none / shadow / blur / parallax / layered
    accent_treatment: str = "minimal"        # none / minimal_line / glow / wash / bold_block
    noise_presence: bool = False
    glass_presence: bool = False
    overlay_usage: str = "none"              # none / subtle / prominent
    corner_treatment: str = "rounded"        # sharp / subtle_rounded / rounded / pill
    notes: str = ""


@dataclass
class EmotionalObservation:
    """Raw emotional observations from a reference."""
    primary_mood: str = "confident"          # confident / calm / urgent / warm / dramatic / precise
    pacing_character: str = "measured"       # rushed / brisk / measured / slow / paused
    tension_profile: str = "flat"            # flat / building / peak_valley / sustained_high / gentle
    gravitas_level: int = 3                  # 1-5
    energy_level: int = 3                    # 1-5
    warmth_level: int = 2                    # 1-5
    notes: str = ""


@dataclass
class AestheticObservations:
    """Complete set of raw observations extracted from a reference.

    This is the output of style_extractor.py — the raw material
    that aesthetic_parser.py normalizes into runtime semantics.
    """
    source: str = ""                         # source reference identifier
    brand: str = ""                          # Apple / Stripe / Linear / etc.
    typography: TypographyObservation = field(default_factory=TypographyObservation)
    color: ColorObservation = field(default_factory=ColorObservation)
    spacing: SpacingObservation = field(default_factory=SpacingObservation)
    composition: CompositionObservation = field(default_factory=CompositionObservation)
    motion: MotionObservation = field(default_factory=MotionObservation)
    surface: SurfaceObservation = field(default_factory=SurfaceObservation)
    emotional: EmotionalObservation = field(default_factory=EmotionalObservation)
    evaluation_score: int = 0                # from checklist (0-50)
    extractor_confidence: float = 0.5        # 0-1, how confident the extraction is
    raw_notes: str = ""


# ============================================================================
# NormalizedAestheticSemantics — parsed into runtime-mapped profiles
# ============================================================================

@dataclass
class TypographyProfile:
    """Typography normalized to near-style-pack fields."""
    title_font: str = ""
    body_font: str = ""
    scale_mega: int = 84
    scale_display: int = 64
    scale_hero: int = 48
    scale_h1: int = 36
    scale_h2: int = 28
    scale_body: int = 16
    headline_weight: int = 600
    body_weight: int = 400
    tracking: float = -0.01
    line_height_title: float = 1.1
    line_height_body: float = 1.5
    max_width_ch: int = 55
    alignment_dominant: str = "left"
    role_overrides: dict = field(default_factory=dict)


@dataclass
class ColorProfile:
    """Color palette normalized to near-style-pack fields."""
    primary: str = "#333333"
    primary_light: str = "#666666"
    primary_dark: str = "#111111"
    accent: str = "#0066CC"
    accent_light: str = "#40A0FF"
    accent_dark: str = "#004499"
    surface_bg: str = "#FFFFFF"
    surface_neutral: str = "#F5F5F5"
    surface_dark: str = "#111111"
    surface_mid: str = "#2A2A2A"
    text_primary: str = "#1A1A1A"
    text_secondary: str = "#666666"
    text_tertiary: str = "#999999"
    text_on_dark: str = "#F0F0F0"
    text_on_dark_secondary: str = "rgba(240,240,240,0.7)"
    text_on_brand: str = "#FFFFFF"
    text_on_brand_secondary: str = "rgba(255,255,255,0.8)"
    mood: str = "neutral"
    saturation: str = "low"


@dataclass
class MotionProfile:
    """Motion language normalized to near-style-pack fields."""
    default_easing: str = "cubic-bezier(0.22, 0, 0, 1)"
    entrance_base_stagger: int = 150
    entrance_style: str = "fade_up"
    speed_moderate: float = 1.0
    speed_fast: float = 0.5
    speed_slow: float = 1.8
    scale_variation_enabled: bool = False
    transition_default_type: str = "slide_fade"
    transition_default_duration: int = 500
    emotional_entrance_overrides: dict = field(default_factory=dict)


@dataclass
class CompositionProfile:
    """Composition normalized to near-style-pack fields."""
    default_negative_space: float = 0.30
    hook_negative_space: float = 0.50
    conflict_negative_space: float = 0.12
    cta_negative_space: float = 0.55
    default_asymmetry: str = "balanced"
    focal_strategy: str = "single_center"
    depth_layers_default: list = field(default_factory=lambda: ["ambient_glow", "foreground_text"])
    role_layer_overrides: dict = field(default_factory=dict)
    container_class_overrides: dict = field(default_factory=dict)


@dataclass
class SurfaceProfile:
    """Surface system normalized to near-style-pack fields."""
    surface_quality: str = "flat"
    glass_enabled: bool = False
    noise_enabled: bool = False
    glow_enabled: bool = True
    corner_radius: str = "12px"
    background_overrides: dict = field(default_factory=dict)
    surface_overrides: dict = field(default_factory=dict)


@dataclass
class NormalizedAestheticSemantics:
    """Complete normalized semantic profile ready for style pack generation.

    This is the output of aesthetic_parser.py — every field maps
    directly to a style pack system. The generator uses this to
    produce concrete style.json files.
    """
    source: str = ""
    style_name: str = ""
    style_description: str = ""
    inherits: Optional[str] = None

    typography: TypographyProfile = field(default_factory=TypographyProfile)
    color: ColorProfile = field(default_factory=ColorProfile)
    motion: MotionProfile = field(default_factory=MotionProfile)
    composition: CompositionProfile = field(default_factory=CompositionProfile)
    surface: SurfaceProfile = field(default_factory=SurfaceProfile)

    # Additional presets
    spacing_unit: int = 8
    default_intensity: int = 3
    density_overrides: dict = field(default_factory=dict)
    rhythm_overrides: dict = field(default_factory=dict)
    emotional_overrides: dict = field(default_factory=dict)

    metadata_tags: list = field(default_factory=list)
    metadata_best_for: list = field(default_factory=list)
    metadata_avoid_for: list = field(default_factory=list)

    confidence: float = 0.5


# ============================================================================
# Style Scores
# ============================================================================

@dataclass
class DimensionScore:
    """Score for a single quality dimension."""
    name: str = ""
    score: float = 0.0           # 0-100
    weight: float = 1.0          # relative importance
    remarks: str = ""


@dataclass
class StyleScores:
    """Complete scoring result for a style pack."""
    style_name: str = ""
    overall: float = 0.0         # 0-100 weighted average
    dimensions: list = field(default_factory=list)
    breakdown: dict = field(default_factory=dict)
    passed: bool = False
    threshold: float = 60.0


# ============================================================================
# Benchmark Report
# ============================================================================

@dataclass
class BenchmarkReport:
    """Comparison report across multiple style packs."""
    state_title: str = ""
    style_results: list = field(default_factory=list)  # list of {style_name, scores, file_path, size_kb}
    comparison_notes: str = ""
    generated_at: str = ""
