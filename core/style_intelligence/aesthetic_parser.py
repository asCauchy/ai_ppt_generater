"""Aesthetic Parser — AestheticObservations → NormalizedAestheticSemantics.

Converts raw extracted observations into normalized runtime semantics.
This is the bridge between "what we see" and "what the style system needs."

Each sub-parser maps observation fields to the corresponding profile
fields that the style_pack_generator will use to produce style.json.

Design principle: the parser resolves ambiguity, fills gaps with
sensible defaults, and normalizes heterogeneous descriptions into
consistent runtime language.
"""

from __future__ import annotations

from .aesthetic_models import (
    AestheticObservations,
    TypographyObservation, ColorObservation, SpacingObservation,
    CompositionObservation, MotionObservation, SurfaceObservation,
    EmotionalObservation,
    NormalizedAestheticSemantics,
    TypographyProfile, ColorProfile, MotionProfile,
    CompositionProfile, SurfaceProfile,
)


class AestheticParser:
    """Parse extracted observations into normalized runtime semantics."""

    def parse(self, observations: AestheticObservations) -> NormalizedAestheticSemantics:
        """Convert observations to normalized semantics ready for style pack generation."""
        sem = NormalizedAestheticSemantics()

        # Identity
        sem.source = observations.source
        sem.style_name = self._derive_style_name(observations)
        sem.style_description = self._derive_description(observations)
        sem.confidence = observations.extractor_confidence

        # Sub-parsers
        sem.typography = self._parse_typography(observations.typography, observations)
        sem.color = self._parse_color(observations.color, observations)
        sem.motion = self._parse_motion(observations.motion, observations)
        sem.composition = self._parse_composition(observations.composition, observations)
        sem.surface = self._parse_surface(observations.surface, observations)

        # Derived presets
        sem.spacing_unit = self._derive_spacing_unit(observations.spacing)
        sem.default_intensity = observations.emotional.energy_level
        sem.density_overrides = self._derive_density(observations)
        sem.rhythm_overrides = self._derive_rhythm(observations.emotional)
        sem.emotional_overrides = self._derive_emotional_overrides(observations)

        # Metadata
        sem.metadata_tags = self._derive_tags(observations)
        sem.metadata_best_for, sem.metadata_avoid_for = self._derive_usage(observations)

        return sem

    # ------------------------------------------------------------------
    # Typography parser
    # ------------------------------------------------------------------

    def _parse_typography(self, obs: TypographyObservation,
                           full: AestheticObservations) -> TypographyProfile:
        profile = TypographyProfile()

        # Font stacks
        if obs.font_character == "serif":
            profile.title_font = "Noto Serif SC, Source Han Serif SC, Georgia, serif"
            profile.body_font = "Noto Sans SC, Source Han Sans SC, system-ui, sans-serif"
        elif obs.font_character == "mono":
            profile.title_font = "'SF Mono', 'Fira Code', 'JetBrains Mono', monospace"
            profile.body_font = "system-ui, -apple-system, sans-serif"
        elif obs.font_character == "sans_humanist":
            profile.title_font = "system-ui, -apple-system, 'Segoe UI', sans-serif"
            profile.body_font = "system-ui, -apple-system, 'Segoe UI', sans-serif"
        else:  # sans_geometric (default)
            profile.title_font = "SF Pro Display, system-ui, -apple-system, sans-serif"
            profile.body_font = "SF Pro Text, system-ui, -apple-system, sans-serif"

        # Override with explicit hints
        if obs.title_font_hint:
            profile.title_font = obs.title_font_hint
        if obs.body_font_hint:
            profile.body_font = obs.body_font_hint

        # Scale from contrast ratio
        ratio = obs.scale_contrast
        if ratio >= 5.0:
            profile.scale_mega = 96
            profile.scale_display = 72
            profile.scale_hero = 56
            profile.scale_h1 = 42
            profile.scale_h2 = 28
            profile.scale_body = 16
        elif ratio >= 3.5:
            profile.scale_mega = 84
            profile.scale_display = 64
            profile.scale_hero = 48
            profile.scale_h1 = 36
            profile.scale_h2 = 28
            profile.scale_body = 16
        elif ratio >= 2.5:
            profile.scale_mega = 72
            profile.scale_display = 56
            profile.scale_hero = 44
            profile.scale_h1 = 32
            profile.scale_h2 = 24
            profile.scale_body = 16
        else:
            profile.scale_mega = 64
            profile.scale_display = 48
            profile.scale_hero = 40
            profile.scale_h1 = 32
            profile.scale_h2 = 24
            profile.scale_body = 16

        # Weight
        profile.headline_weight = obs.headline_weight
        profile.body_weight = obs.body_weight

        # Tracking
        if obs.tracking_character == "tight":
            profile.tracking = -0.025
        elif obs.tracking_character == "wide":
            profile.tracking = 0.01
        else:
            profile.tracking = -0.01

        # Line height
        profile.line_height_title = 1.08 if obs.hierarchy_depth >= 4 else 1.12
        profile.line_height_body = obs.line_height_ratio

        # Max width
        profile.max_width_ch = obs.max_line_length_ch

        # Alignment
        profile.alignment_dominant = obs.alignment_dominant

        # Role overrides from hierarchy depth
        if obs.hierarchy_depth >= 4:
            profile.role_overrides = {
                "hook": {"title_weight": 800, "title_tracking": -0.025},
                "call_to_action": {"title_weight": 800, "title_tracking": -0.025},
            }
        elif obs.hierarchy_depth <= 2:
            profile.role_overrides = {
                "hook": {"title_weight": 600, "title_tracking": -0.01},
                "breathing_page": {"title_weight": 300},
            }

        return profile

    # ------------------------------------------------------------------
    # Color parser
    # ------------------------------------------------------------------

    def _parse_color(self, obs: ColorObservation,
                      full: AestheticObservations) -> ColorProfile:
        profile = ColorProfile()

        profile.primary = obs.primary_hex
        profile.accent = obs.accent_hex
        profile.surface_bg = obs.background_hex
        profile.surface_neutral = obs.surface_hex
        profile.text_primary = obs.text_primary_hex
        profile.text_secondary = obs.text_secondary_hex

        # Derive light/dark variants
        profile.primary_light = self._lighten_hex(obs.primary_hex, 0.35)
        profile.primary_dark = self._darken_hex(obs.primary_hex, 0.4)
        profile.accent_light = self._lighten_hex(obs.accent_hex, 0.35)
        profile.accent_dark = self._darken_hex(obs.accent_hex, 0.4)

        # Surface dark/mid
        profile.surface_dark = self._darken_hex(obs.background_hex, 0.9)
        profile.surface_mid = self._darken_hex(obs.background_hex, 0.7)

        # Text on dark
        profile.text_on_dark = self._lighten_hex(obs.background_hex, 0.9)
        profile.text_on_dark_secondary = f"rgba({self._hex_to_rgb_str(self._lighten_hex(obs.background_hex, 0.9))}, 0.7)"

        # Text on brand
        profile.text_on_brand = "#FFFFFF"
        profile.text_on_brand_secondary = "rgba(255,255,255,0.8)"

        # Mood
        profile.mood = obs.mood
        profile.saturation = obs.saturation_level

        return profile

    # ------------------------------------------------------------------
    # Motion parser
    # ------------------------------------------------------------------

    def _parse_motion(self, obs: MotionObservation,
                       full: AestheticObservations) -> MotionProfile:
        profile = MotionProfile()

        # Easing
        easing_map = {
            "ease_out": "cubic-bezier(0.25, 0.1, 0.25, 1)",
            "ease_in_out": "cubic-bezier(0.4, 0, 0.2, 1)",
            "spring": "cubic-bezier(0, 0.55, 0.45, 1)",
            "linear": "cubic-bezier(0, 0, 1, 1)",
            "custom": "cubic-bezier(0.22, 0, 0, 1)",
        }
        profile.default_easing = easing_map.get(obs.easing_philosophy,
                                                  easing_map["ease_out"])

        # Stagger
        stagger_map = {
            "sequential": 120,
            "wave": 150,
            "staggered": 200,
            "simultaneous": 0,
            "none": 80,
        }
        profile.entrance_base_stagger = stagger_map.get(obs.stagger_character, 150)

        # Entrance style
        entrance_map = {
            "fade": "active_reveal",
            "fade_up": "active_reveal",
            "scale": "scale_reveal",
            "slide": "drive_forward",
            "masked_reveal": "delayed_reveal",
            "cut": "impact_reveal",
        }
        profile.entrance_style = entrance_map.get(obs.entrance_style, "active_reveal")

        # Speed
        if obs.speed_range == "slow":
            profile.speed_moderate = 1.5
            profile.speed_fast = 0.8
            profile.speed_slow = 2.5
        elif obs.speed_range == "fast":
            profile.speed_moderate = 0.6
            profile.speed_fast = 0.3
            profile.speed_slow = 1.2
        else:
            profile.speed_moderate = 1.0
            profile.speed_fast = 0.5
            profile.speed_slow = 1.8

        # Scale variation
        profile.scale_variation_enabled = obs.scale_variation_presence

        # Transition
        trans_map = {
            "hard_cut": ("hard_cut", 150),
            "dissolve": ("slide_fade", 500),
            "push": ("slide_fade", 400),
            "morph": ("morph_deepen", 800),
            "zoom": ("zoom_example", 500),
        }
        trans_type, trans_dur = trans_map.get(obs.transition_style,
                                                ("slide_fade", 500))
        profile.transition_default_type = trans_type
        profile.transition_default_duration = trans_dur

        # Emotional entrance overrides from emotional profile
        emotional = full.emotional
        if emotional.energy_level >= 4:
            profile.emotional_entrance_overrides = {
                "excited": {"stagger_ms": 80, "easing": "emphatic"},
                "determined": {"stagger_ms": 80, "easing": "snappy"},
            }
        elif emotional.energy_level <= 2:
            profile.emotional_entrance_overrides = {
                "reflective": {"stagger_ms": 500, "easing": "gentle"},
                "solemn": {"stagger_ms": 600, "easing": "gentle"},
            }

        return profile

    # ------------------------------------------------------------------
    # Composition parser
    # ------------------------------------------------------------------

    def _parse_composition(self, obs: CompositionObservation,
                            full: AestheticObservations) -> CompositionProfile:
        profile = CompositionProfile()

        # Negative space
        spacing = full.spacing
        profile.default_negative_space = spacing.whitespace_ratio

        # Role-specific negative space
        if spacing.whitespace_ratio > 0.45:
            profile.hook_negative_space = 0.55
            profile.conflict_negative_space = 0.15
            profile.cta_negative_space = 0.60
        elif spacing.whitespace_ratio > 0.25:
            profile.hook_negative_space = 0.45
            profile.conflict_negative_space = 0.12
            profile.cta_negative_space = 0.50
        else:
            profile.hook_negative_space = 0.35
            profile.conflict_negative_space = 0.08
            profile.cta_negative_space = 0.40

        # Asymmetry
        asym_map = {
            "symmetric": "symmetric",
            "balanced": "balanced",
            "slight": "slight_left",
            "dynamic": "dynamic_shift",
            "unbalanced": "unbalanced",
        }
        profile.default_asymmetry = asym_map.get(obs.asymmetry_level, "balanced")

        # Focal strategy
        profile.focal_strategy = obs.focal_strategy

        # Depth layers
        if obs.depth_layers >= 4:
            profile.depth_layers_default = [
                "ambient_glow", "accent_wash", "foreground_text", "accent_dust"
            ]
        elif obs.depth_layers >= 3:
            profile.depth_layers_default = [
                "ambient_glow", "surface_panel", "foreground_text"
            ]
        else:
            profile.depth_layers_default = ["ambient_glow", "foreground_text"]

        # Layer overrides for specific roles
        if obs.background_treatment == "atmospheric":
            profile.role_layer_overrides = {
                "vision": ["horizon_gradient", "glow_sphere", "foreground_text", "accent_dust"],
                "hook": ["ambient_glow", "glow_sphere", "foreground_text", "accent_line"],
            }

        return profile

    # ------------------------------------------------------------------
    # Surface parser
    # ------------------------------------------------------------------

    def _parse_surface(self, obs: SurfaceObservation,
                        full: AestheticObservations) -> SurfaceProfile:
        profile = SurfaceProfile()

        profile.surface_quality = obs.surface_quality
        profile.glass_enabled = obs.glass_presence
        profile.noise_enabled = obs.noise_presence

        # Glow
        profile.glow_enabled = obs.accent_treatment in ("glow", "wash")

        # Corner radius
        corner_map = {
            "sharp": "4px",
            "subtle_rounded": "8px",
            "rounded": "12px",
            "pill": "24px",
        }
        profile.corner_radius = corner_map.get(obs.corner_treatment, "12px")

        # Background overrides from surface quality
        bg_override_map = {
            "flat": {},
            "subtle_gradient": {
                "brand_gradient": "linear-gradient(180deg, var(--c-primary) 0%, var(--c-surface-mid) 100%)",
                "horizon_gradient": "linear-gradient(180deg, var(--c-surface-bg) 0%, color-mix(in srgb, var(--c-accent) 8%, var(--c-surface-bg)) 50%, var(--c-surface-bg) 100%)",
            },
            "gradient": {
                "brand_gradient": "linear-gradient(135deg, var(--c-primary) 0%, var(--c-primary-light) 100%)",
                "dark_gradient": "linear-gradient(170deg, var(--c-surface-dark) 0%, var(--c-surface-mid) 40%, var(--c-primary-dark) 100%)",
            },
            "glass": {
                "brand_gradient": "var(--c-surface-dark)",
                "dark_gradient": "var(--c-surface-dark)",
            },
            "textured": {
                "brand_gradient": "var(--c-primary)",
                "dark_gradient": "var(--c-surface-dark)",
            },
            "atmospheric": {
                "brand_gradient": "radial-gradient(ellipse at 50% 40%, var(--c-primary-dark) 0%, var(--c-surface-dark) 70%)",
                "horizon_gradient": "radial-gradient(ellipse at 50% 30%, var(--c-surface-bg) 0%, color-mix(in srgb, var(--c-accent) 10%, var(--c-surface-bg)) 60%, var(--c-surface-bg) 100%)",
            },
        }
        profile.background_overrides = bg_override_map.get(obs.surface_quality, {})

        # Surface overrides per role
        if obs.depth_treatment == "shadow":
            profile.surface_overrides = {
                "evidence": {"ambient": "none"},
                "recap": {"ambient": "none"},
            }
        elif obs.depth_treatment == "blur":
            profile.surface_overrides = {
                "insight": {"ambient": "glow", "accent_glow": True},
                "vision": {"ambient": "glow", "accent_glow": True},
            }

        return profile

    # ------------------------------------------------------------------
    # Derivation helpers
    # ------------------------------------------------------------------

    def _derive_style_name(self, obs: AestheticObservations) -> str:
        """Generate a style pack name from observations."""
        brand = obs.brand.lower().replace(" ", "_") if obs.brand else "custom"
        mood = obs.emotional.primary_mood.lower().replace(" ", "_")

        # Avoid overly long names
        if brand and mood and brand != "unknown":
            return f"{brand}_{mood}"
        return f"extracted_{mood}"

    def _derive_description(self, obs: AestheticObservations) -> str:
        """Generate a human-readable description."""
        brand_str = f"{obs.brand}-inspired" if obs.brand else "Custom"
        mood_str = obs.emotional.primary_mood
        surface_str = obs.surface.surface_quality.replace("_", " ")
        return (
            f"{brand_str} style with {mood_str} emotional register. "
            f"{obs.typography.font_character.replace('_', ' ')} typography, "
            f"{surface_str} surfaces, {obs.spacing.padding_character} spacing."
        )

    def _derive_spacing_unit(self, spacing: SpacingObservation) -> int:
        """Derive base spacing unit from observations."""
        if spacing.padding_character == "luxurious":
            return 12
        elif spacing.padding_character == "generous":
            return 8
        elif spacing.padding_character == "tight":
            return 4
        return 8

    def _derive_density(self, obs: AestheticObservations) -> dict:
        """Derive density level overrides."""
        if obs.spacing.density_feel == "sparse":
            return {
                "1": {"max_points": 2, "max_chars_per_point": 35, "max_total_chars": 45},
                "3": {"max_points": 3, "max_chars_per_point": 65, "max_total_chars": 150},
            }
        elif obs.spacing.density_feel == "dense" or obs.spacing.density_feel == "packed":
            return {
                "3": {"max_points": 5, "max_chars_per_point": 90, "max_total_chars": 280},
                "5": {"max_points": 8, "max_chars_per_point": 120, "max_total_chars": 550},
            }
        return {}

    def _derive_rhythm(self, emotional: EmotionalObservation) -> dict:
        """Derive cinematic rhythm overrides."""
        rhythm = {}
        if emotional.tension_profile == "building":
            rhythm["tension_curve"] = [
                {"position_pct": 0, "intensity": 3},
                {"position_pct": 30, "intensity": 4},
                {"position_pct": 60, "intensity": 5},
                {"position_pct": 80, "intensity": 5},
                {"position_pct": 100, "intensity": 4},
            ]
        elif emotional.tension_profile == "peak_valley":
            rhythm["tension_curve"] = [
                {"position_pct": 0, "intensity": 4},
                {"position_pct": 25, "intensity": 2},
                {"position_pct": 50, "intensity": 5},
                {"position_pct": 75, "intensity": 2},
                {"position_pct": 100, "intensity": 5},
            ]
        elif emotional.tension_profile == "sustained_high":
            rhythm["act_pacing"] = {
                "opening": {"pace": "moderate", "intensity_baseline": 4},
                "climax": {"pace": "fast", "intensity_baseline": 5},
                "closing": {"pace": "slow", "intensity_baseline": 5},
            }
        return rhythm

    def _derive_emotional_overrides(self, obs: AestheticObservations) -> dict:
        """Derive emotional mapping overrides."""
        overrides = {}
        emotional = obs.emotional

        if emotional.warmth_level >= 4:
            overrides["hopeful"] = {"emphasis_delay": 0.4, "weight_keywords": True}
            overrides["inspired"] = {"emphasis_delay": 0.3, "weight_keywords": True}

        if emotional.gravitas_level >= 4:
            overrides["solemn"] = {"emphasis_delay": 0.8, "weight_keywords": False}
            overrides["determined"] = {"emphasis_delay": 0.15, "weight_keywords": True}

        return overrides

    def _derive_tags(self, obs: AestheticObservations) -> list:
        """Generate metadata tags."""
        tags = []
        if obs.brand:
            tags.append(obs.brand.lower())
        tags.append(obs.emotional.primary_mood)
        tags.append(obs.typography.font_character.replace("_", " "))
        tags.append(obs.surface.surface_quality.replace("_", " "))
        if obs.spacing.whitespace_ratio > 0.4:
            tags.append("spacious")
        if obs.spacing.whitespace_ratio < 0.2:
            tags.append("dense")
        return tags

    def _derive_usage(self, obs: AestheticObservations) -> tuple:
        """Derive best_for and avoid_for lists."""
        best_for = []
        avoid_for = []

        mood = obs.emotional.primary_mood
        ws = obs.spacing.whitespace_ratio

        if mood in ("confident", "precise"):
            best_for.extend(["executive_presentations", "product_keynotes", "design_reviews"])
        elif mood in ("dramatic", "urgent"):
            best_for.extend(["large_venue_keynotes", "strategic_announcements"])
            avoid_for.extend(["casual_meetings", "academic_seminars"])
        elif mood in ("calm", "warm"):
            best_for.extend(["academic_seminars", "team_briefings"])
            avoid_for.extend(["high_energy_pitches"])

        if ws > 0.4:
            best_for.append("brand_films")
        elif ws < 0.18:
            best_for.append("data_dense_reports")
            avoid_for.append("brand_films")

        return (best_for, avoid_for)

    # ------------------------------------------------------------------
    # Color math helpers (simple, no dependencies)
    # ------------------------------------------------------------------

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        return (int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16))

    def _hex_to_rgb_str(self, hex_color: str) -> str:
        r, g, b = self._hex_to_rgb(hex_color)
        return f"{r},{g},{b}"

    def _darken_hex(self, hex_color: str, amount: float) -> str:
        r, g, b = self._hex_to_rgb(hex_color)
        r, g, b = int(r * amount), int(g * amount), int(b * amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lighten_hex(self, hex_color: str, amount: float) -> str:
        r, g, b = self._hex_to_rgb(hex_color)
        r = int(r + (255 - r) * amount)
        g = int(g + (255 - g) * amount)
        b = int(b + (255 - b) * amount)
        return f"#{r:02x}{g:02x}{b:02x}"
