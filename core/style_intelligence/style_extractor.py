"""Style Extractor — reference observations → AestheticObservations.

Parses structured reference distillations (from the references/ framework)
and produces AestheticObservations — the raw material for the parser.

Input formats supported:
  1. Distillation dict (from distillation_template.md filled in)
  2. Direct observation dict
  3. Reference evaluation checklist result

The extractor normalizes heterogeneous input into a single structured
AestheticObservations dataclass.
"""

from __future__ import annotations

from .aesthetic_models import (
    AestheticObservations,
    TypographyObservation,
    ColorObservation,
    SpacingObservation,
    CompositionObservation,
    MotionObservation,
    SurfaceObservation,
    EmotionalObservation,
)


class StyleExtractor:
    """Extract structured aesthetic observations from reference descriptions."""

    def extract_from_distillation(self, distillation: dict) -> AestheticObservations:
        """Parse a filled distillation template into observations."""
        obs = AestheticObservations()
        obs.source = distillation.get("source", distillation.get("Source", ""))
        obs.brand = distillation.get("brand", distillation.get("Brand", ""))

        # Motion Grammar section
        motion_grammar = distillation.get("motion_grammar", {})
        if not motion_grammar:
            motion_grammar = {
                "easing": distillation.get("easing_philosophy", ""),
                "stagger": distillation.get("stagger_pattern", ""),
                "speed": distillation.get("speed_range", ""),
            }

        obs.motion = self._extract_motion(motion_grammar, distillation)

        # Transition section
        trans = distillation.get("transition_type", distillation.get("transitions", {}))
        if isinstance(trans, str):
            trans = {"primary": trans}
        obs.motion.transition_style = trans.get("primary", "dissolve")

        # Composition section
        comp = distillation.get("composition_pattern", distillation.get("composition", {}))
        obs.composition = self._extract_composition(comp)

        # Typography section
        typo = distillation.get("typography_pattern", distillation.get("typography", {}))
        obs.typography = self._extract_typography(typo)

        # Emotional section
        emotional = distillation.get("emotional_effect", distillation.get("emotional", {}))
        obs.emotional = self._extract_emotional(emotional)

        # Color (inferred from brand and emotional profile)
        obs.color = self._infer_color_from_brand(obs.brand, distillation)

        # Spacing (inferred from composition and typography)
        obs.spacing = self._infer_spacing(obs.composition, obs.typography)

        # Surface (inferred from brand and composition)
        obs.surface = self._infer_surface(obs.brand, obs.composition)

        # Evaluation score
        score = distillation.get("evaluation_score", distillation.get("Evaluation Score", 0))
        try:
            obs.evaluation_score = int(score) if score else 0
        except (ValueError, TypeError):
            obs.evaluation_score = 0

        obs.extractor_confidence = self._confidence(obs)
        return obs

    def extract_from_observations(self, raw: dict) -> AestheticObservations:
        """Direct extraction from a structured observation dict."""
        obs = AestheticObservations()
        obs.source = raw.get("source", "")
        obs.brand = raw.get("brand", "")

        if "typography" in raw:
            obs.typography = TypographyObservation(**{k: v for k, v in raw["typography"].items()
                if k in TypographyObservation.__dataclass_fields__})
        if "color" in raw:
            obs.color = ColorObservation(**{k: v for k, v in raw["color"].items()
                if k in ColorObservation.__dataclass_fields__})
        if "spacing" in raw:
            obs.spacing = SpacingObservation(**{k: v for k, v in raw["spacing"].items()
                if k in SpacingObservation.__dataclass_fields__})
        if "composition" in raw:
            obs.composition = CompositionObservation(**{k: v for k, v in raw["composition"].items()
                if k in CompositionObservation.__dataclass_fields__})
        if "motion" in raw:
            obs.motion = MotionObservation(**{k: v for k, v in raw["motion"].items()
                if k in MotionObservation.__dataclass_fields__})
        if "surface" in raw:
            obs.surface = SurfaceObservation(**{k: v for k, v in raw["surface"].items()
                if k in SurfaceObservation.__dataclass_fields__})
        if "emotional" in raw:
            obs.emotional = EmotionalObservation(**{k: v for k, v in raw["emotional"].items()
                if k in EmotionalObservation.__dataclass_fields__})

        obs.evaluation_score = raw.get("evaluation_score", 0)
        obs.extractor_confidence = self._confidence(obs)
        return obs

    # ------------------------------------------------------------------
    # Sub-extractors
    # ------------------------------------------------------------------

    def _extract_motion(self, grammar: dict, full: dict) -> MotionObservation:
        obs = MotionObservation()

        easing = grammar.get("easing", grammar.get("easing_philosophy", ""))
        if "spring" in str(easing).lower():
            obs.easing_philosophy = "spring"
        elif "ease-in-out" in str(easing) or "ease in out" in str(easing).lower():
            obs.easing_philosophy = "ease_in_out"
        elif "ease-out" in str(easing) or "ease out" in str(easing).lower():
            obs.easing_philosophy = "ease_out"
        elif "linear" in str(easing).lower():
            obs.easing_philosophy = "linear"
        elif "custom" in str(easing).lower():
            obs.easing_philosophy = "custom"

        speed = grammar.get("speed", grammar.get("speed_range", ""))
        if "slow" in str(speed).lower():
            obs.speed_range = "slow"
        elif "fast" in str(speed).lower():
            obs.speed_range = "fast"
        elif "mixed" in str(speed).lower():
            obs.speed_range = "mixed"

        stagger = grammar.get("stagger", grammar.get("stagger_pattern", ""))
        if "wave" in str(stagger).lower():
            obs.stagger_character = "wave"
        elif "sequential" in str(stagger).lower():
            obs.stagger_character = "sequential"
        elif "simultaneous" in str(stagger).lower():
            obs.stagger_character = "simultaneous"
        elif "none" in str(stagger).lower():
            obs.stagger_character = "none"

        # Entrance style from composition pattern
        comp = full.get("composition_pattern", full.get("composition", {}))
        focal = comp.get("focal_point", comp.get("focal", ""))
        if "center" in str(focal).lower():
            obs.entrance_style = "fade_up"

        transition = full.get("transition_type", full.get("transitions", {}))
        if isinstance(transition, dict):
            obs.transition_style = transition.get("primary", "dissolve")
        elif isinstance(transition, str):
            obs.transition_style = transition

        scale = grammar.get("scale_variation", 0)
        obs.scale_variation_presence = bool(scale)

        # Motion density from speed and stagger
        if obs.speed_range == "fast" and obs.stagger_character in ("sequential", "wave"):
            obs.motion_density = "rich"
        elif obs.speed_range == "slow":
            obs.motion_density = "sparse"

        return obs

    def _extract_composition(self, comp: dict) -> CompositionObservation:
        obs = CompositionObservation()

        focal = comp.get("focal_point", comp.get("focal", ""))
        fp = str(focal).lower()
        if "center" in fp or "absolute" in fp:
            obs.focal_strategy = "single_center"
        elif "split" in fp or "left" in fp:
            obs.focal_strategy = "split"
        elif "diagonal" in fp:
            obs.focal_strategy = "diagonal"
        elif "fragmented" in fp:
            obs.focal_strategy = "fragmented"

        grid = comp.get("grid_structure", comp.get("grid", ""))
        if "asymmetrical" in str(grid).lower() or "asymmetric" in str(grid).lower():
            obs.asymmetry_level = "dynamic"
        elif "symmetrical" in str(grid).lower() or "centered" in str(grid).lower():
            obs.asymmetry_level = "balanced"

        depth = comp.get("depth_layers", comp.get("depth", 2))
        try:
            obs.depth_layers = int(depth) if depth else 2
        except (ValueError, TypeError):
            obs.depth_layers = 2

        elem_count = comp.get("element_count", comp.get("elements", "few"))
        obs.element_count_per_frame = str(elem_count)

        bg = comp.get("background", comp.get("background_treatment", ""))
        if "gradient" in str(bg).lower():
            obs.background_treatment = "gradient"
        elif "image" in str(bg).lower():
            obs.background_treatment = "image"
        elif "textured" in str(bg).lower():
            obs.background_treatment = "textured"
        elif "atmospheric" in str(bg).lower():
            obs.background_treatment = "atmospheric"

        return obs

    def _extract_typography(self, typo: dict) -> TypographyObservation:
        obs = TypographyObservation()

        # Font identification
        fonts = typo.get("fonts", typo.get("font", ""))
        if isinstance(fonts, list):
            fonts = ", ".join(fonts)
        fonts_lower = str(fonts).lower()
        if "serif" in fonts_lower and ("sans" not in fonts_lower):
            obs.font_character = "serif"
        elif "mono" in fonts_lower:
            obs.font_character = "mono"
        elif "geometric" in fonts_lower:
            obs.font_character = "sans_geometric"
        elif "humanist" in fonts_lower:
            obs.font_character = "sans_humanist"

        obs.title_font_hint = typo.get("title_font", typo.get("fonts", ""))
        if isinstance(obs.title_font_hint, list):
            obs.title_font_hint = obs.title_font_hint[0] if obs.title_font_hint else ""

        # Scale
        scale_range = typo.get("scale_range", typo.get("scale", ""))
        obs.scale_contrast = 3.0  # default
        if "hero" in str(scale_range).lower() or "display" in str(scale_range).lower():
            obs.scale_contrast = 4.5

        # Weight
        weight_contrast = typo.get("weight_contrast", typo.get("weight", ""))
        if "bold" in str(weight_contrast).lower() or "multi" in str(weight_contrast).lower():
            obs.headline_weight = 700

        # Reveal behavior
        reveal = typo.get("reveal_behavior", typo.get("reveal", ""))
        if "word" in str(reveal).lower():
            obs.hierarchy_depth = 3
        elif "line" in str(reveal).lower():
            obs.hierarchy_depth = 2
        elif "character" in str(reveal).lower() or "char" in str(reveal).lower():
            obs.hierarchy_depth = 4

        # Alignment
        align = typo.get("alignment", "")
        if "center" in str(align).lower():
            obs.alignment_dominant = "center"
        elif "right" in str(align).lower():
            obs.alignment_dominant = "right"

        return obs

    def _extract_emotional(self, emotional: dict) -> EmotionalObservation:
        obs = EmotionalObservation()

        primary = str(emotional.get("primary_emotion", emotional.get("primary", ""))).lower()
        mood_map = {
            "confidence": "confident", "wonder": "warm", "precision": "precise",
            "warmth": "warm", "urgency": "urgent", "calm": "calm",
            "excitement": "dramatic", "gravitas": "dramatic",
        }
        obs.primary_mood = mood_map.get(primary, primary if primary else "confident")

        tension = str(emotional.get("tension_profile", emotional.get("tension", ""))).lower()
        if "building" in tension or "intensity" in tension:
            obs.tension_profile = "building"
        elif "peak" in tension:
            obs.tension_profile = "peak_valley"
        elif "sustained" in tension:
            obs.tension_profile = "sustained_high"
        elif "gentle" in tension:
            obs.tension_profile = "gentle"

        # Gravitas from score
        score = emotional.get("evaluation_score", 35)
        try:
            score_val = int(score) if score else 35
        except (ValueError, TypeError):
            score_val = 35
        obs.gravitas_level = min(5, max(1, score_val // 10))

        obs.notes = emotional.get("how", emotional.get("notes", ""))
        return obs

    # ------------------------------------------------------------------
    # Inference helpers — fill gaps when data is sparse
    # ------------------------------------------------------------------

    def _infer_color_from_brand(self, brand: str, distillation: dict) -> ColorObservation:
        """Infer color palette from brand identity and emotional cues."""
        obs = ColorObservation()

        brand_palettes = {
            "apple": {
                "primary_hex": "#1D1D1F", "accent_hex": "#0071E3",
                "background_hex": "#FFFFFF", "surface_hex": "#F5F5F7",
                "mood": "neutral", "saturation_level": "low",
                "gradient_presence": "minimal", "dark_mode": False,
            },
            "stripe": {
                "primary_hex": "#635BFF", "accent_hex": "#00D924",
                "background_hex": "#FFFFFF", "surface_hex": "#F6F9FC",
                "mood": "cool", "saturation_level": "medium",
                "gradient_presence": "prominent", "dark_mode": True,
            },
            "linear": {
                "primary_hex": "#1A1A1A", "accent_hex": "#5E6AD2",
                "background_hex": "#0A0A0A", "surface_hex": "#1A1A1A",
                "mood": "dramatic", "saturation_level": "medium",
                "gradient_presence": "minimal", "dark_mode": True,
            },
            "arc": {
                "primary_hex": "#1C1C1E", "accent_hex": "#FF5F1F",
                "background_hex": "#FFFFFF", "surface_hex": "#F2F2F7",
                "mood": "warm", "saturation_level": "medium",
                "gradient_presence": "prominent", "dark_mode": False,
            },
        }

        brand_key = str(brand).lower()
        for key, palette in brand_palettes.items():
            if key in brand_key:
                for k, v in palette.items():
                    setattr(obs, k, v)
                return obs

        # Generic modern palette
        obs.primary_hex = "#1A1A1A"
        obs.accent_hex = "#0066CC"
        obs.background_hex = "#FFFFFF"
        obs.surface_hex = "#F5F5F5"
        obs.mood = "neutral"
        return obs

    def _infer_spacing(self, comp: CompositionObservation,
                        typo: TypographyObservation) -> SpacingObservation:
        """Infer spacing characteristics from composition + typography."""
        obs = SpacingObservation()

        # Negative space from composition density
        if comp.element_count_per_frame in ("minimal(1-3)", "few(4-6)"):
            obs.whitespace_ratio = 0.55
        elif comp.element_count_per_frame == "moderate(7-10)":
            obs.whitespace_ratio = 0.30
        else:
            obs.whitespace_ratio = 0.15

        # Padding character
        if obs.whitespace_ratio > 0.45:
            obs.padding_character = "luxurious"
        elif obs.whitespace_ratio > 0.30:
            obs.padding_character = "generous"
        elif obs.whitespace_ratio > 0.18:
            obs.padding_character = "moderate"
        else:
            obs.padding_character = "tight"

        # Asymmetry from composition
        if comp.asymmetry_level in ("dynamic", "unbalanced"):
            obs.margin_asymmetry = "unbalanced"
        elif comp.asymmetry_level == "balanced":
            obs.margin_asymmetry = "symmetric"

        # Density
        if obs.whitespace_ratio < 0.15:
            obs.density_feel = "packed"
        elif obs.whitespace_ratio < 0.25:
            obs.density_feel = "dense"
        elif obs.whitespace_ratio > 0.45:
            obs.density_feel = "sparse"

        return obs

    def _infer_surface(self, brand: str, comp: CompositionObservation) -> SurfaceObservation:
        """Infer surface treatment from brand + composition."""
        obs = SurfaceObservation()

        brand_lower = str(brand).lower()
        if "apple" in brand_lower:
            obs.surface_quality = "subtle_gradient"
            obs.depth_treatment = "shadow"
            obs.glass_presence = False
        elif "stripe" in brand_lower:
            obs.surface_quality = "gradient"
            obs.depth_treatment = "layered"
            obs.glass_presence = True
        elif "linear" in brand_lower:
            obs.surface_quality = "glass"
            obs.depth_treatment = "blur"
            obs.glass_presence = True
            obs.noise_presence = True
        elif "arc" in brand_lower:
            obs.surface_quality = "gradient"
            obs.depth_treatment = "parallax"
            obs.glass_presence = True

        if comp.depth_layers >= 3:
            obs.accent_treatment = "glow"
        elif comp.background_treatment == "atmospheric":
            obs.accent_treatment = "wash"

        return obs

    def _confidence(self, obs: AestheticObservations) -> float:
        """Estimate extraction confidence based on data completeness."""
        signals = 0
        total = 7

        if obs.typography.font_character != "sans_geometric" or obs.typography.title_font_hint:
            signals += 1
        if obs.color.primary_hex != "#333333" or obs.brand:
            signals += 1
        if obs.spacing.whitespace_ratio != 0.30:
            signals += 1
        if obs.composition.focal_strategy != "single_center":
            signals += 1
        if obs.motion.easing_philosophy != "ease_out" or obs.brand:
            signals += 1
        if obs.surface.surface_quality != "flat" or obs.brand:
            signals += 1
        if obs.emotional.primary_mood != "confident" or obs.evaluation_score > 0:
            signals += 1

        return min(0.95, signals / total + 0.1)
