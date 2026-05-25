"""Style Pack Generator — NormalizedAestheticSemantics → style.json.

Converts normalized aesthetic semantics into a concrete, loadable
style pack JSON file. This is the final stage of the extraction pipeline.

The generator:
  1. Maps normalized profiles to style pack systems
  2. Fills defaults from the schema where profiles are incomplete
  3. Handles inheritance (generated pack can extend a parent)
  4. Outputs valid, loadable style.json to core/styles/<name>/
"""

from __future__ import annotations

import json
import os
import copy
from typing import Optional

from .aesthetic_models import (
    NormalizedAestheticSemantics,
    TypographyProfile, ColorProfile, MotionProfile,
    CompositionProfile, SurfaceProfile,
)


class StylePackGenerator:
    """Generate style pack JSON from normalized aesthetic semantics."""

    def __init__(self, styles_root: str = None):
        if styles_root is None:
            styles_root = os.path.join(
                os.path.dirname(__file__), "..", "styles"
            )
        self.styles_root = os.path.abspath(styles_root)

    def generate(self, semantics: NormalizedAestheticSemantics) -> dict:
        """Generate a complete style pack dict from normalized semantics."""
        pack = {
            "name": semantics.style_name,
            "version": "1.0",
            "description": semantics.style_description,
        }

        if semantics.inherits:
            pack["inherits"] = semantics.inherits

        # Build each system
        pack["color_system"] = self._build_color_system(semantics.color)
        pack["typography_system"] = self._build_typography_system(semantics.typography)
        pack["composition_system"] = self._build_composition_system(semantics.composition)
        pack["motion_language"] = self._build_motion_language(semantics.motion)
        pack["transition_language"] = self._build_transition_language(semantics.motion)
        pack["surface_system"] = self._build_surface_system(semantics.surface, semantics.color)
        pack["spacing_system"] = self._build_spacing_system(semantics)
        pack["density_system"] = self._build_density_system(semantics)
        pack["emphasis_system"] = self._build_emphasis_system(semantics)
        pack["cinematic_rhythm"] = self._build_cinematic_rhythm(semantics)
        pack["emotional_mapping"] = self._build_emotional_mapping(semantics)

        # Metadata
        pack["metadata"] = {
            "author": "Style Intelligence Pipeline",
            "source": semantics.source,
            "confidence": round(semantics.confidence, 2),
            "tags": semantics.metadata_tags,
            "best_for": semantics.metadata_best_for,
            "avoid_for": semantics.metadata_avoid_for,
        }

        return pack

    def generate_and_save(self, semantics: NormalizedAestheticSemantics,
                           family: str = None) -> str:
        """Generate a style pack and save to disk. Returns the output path.

        If family is specified, saves within that family directory:
          core/styles/<family>/<style_name>/style.json
        Otherwise saves flat:
          core/styles/<style_name>/style.json
        """
        pack = self.generate(semantics)

        if family:
            output_dir = os.path.join(self.styles_root, family, semantics.style_name)
        else:
            output_dir = os.path.join(self.styles_root, semantics.style_name)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, "style.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(pack, f, indent=2, ensure_ascii=False)

        return output_path

    # ==================================================================
    # System builders
    # ==================================================================

    def _build_color_system(self, c: ColorProfile) -> dict:
        return {
            "primary": c.primary,
            "primary_light": c.primary_light,
            "primary_dark": c.primary_dark,
            "accent": c.accent,
            "accent_light": c.accent_light,
            "accent_dark": c.accent_dark,
            "surface_bg": c.surface_bg,
            "surface_neutral": c.surface_neutral,
            "surface_dark": c.surface_dark,
            "surface_mid": c.surface_mid,
            "surface_glass": "rgba(255,255,255,0.08)",
            "surface_raised": c.surface_bg,
            "surface_sunken": c.surface_neutral,
            "text_primary": c.text_primary,
            "text_secondary": c.text_secondary,
            "text_tertiary": c.text_tertiary,
            "text_on_dark": c.text_on_dark,
            "text_on_dark_secondary": c.text_on_dark_secondary,
            "text_on_brand": c.text_on_brand,
            "text_on_brand_secondary": c.text_on_brand_secondary,
            "success": "#22C55E",
            "warning": "#F59E0B",
            "danger": "#EF4444",
            "info": "#3B82F6",
            "glow": f"rgba({self._hex_to_rgb_str(c.accent)}, 0.15)",
            "shadow": "rgba(0,0,0,0.06)",
            "overlay_dark": "rgba(0,0,0,0.4)",
            "overlay_light": "rgba(255,255,255,0.1)",
        }

    def _build_typography_system(self, t: TypographyProfile) -> dict:
        system = {
            "title_font": t.title_font,
            "body_font": t.body_font,
            "mono_font": "'SF Mono', 'Fira Code', monospace",
            "scale_micro": 10,
            "scale_caption": 12,
            "scale_body_sm": 14,
            "scale_body": t.scale_body,
            "scale_body_lg": t.scale_body + 2,
            "scale_h3": int(t.scale_body * 1.4),
            "scale_h2": t.scale_h2,
            "scale_h1": t.scale_h1,
            "scale_hero": t.scale_hero,
            "scale_display": t.scale_display,
            "scale_mega": t.scale_mega,
        }

        # Role prescriptions — selective overrides based on profile
        role_prescriptions = {}
        for role, override in t.role_overrides.items():
            role_prescriptions[role] = override
        if role_prescriptions:
            system["role_prescriptions"] = role_prescriptions

        return system

    def _build_composition_system(self, c: CompositionProfile) -> dict:
        system = {
            "negative_space": {
                "hook": c.hook_negative_space,
                "context": max(0.2, c.default_negative_space - 0.05),
                "evidence": max(0.12, c.default_negative_space - 0.1),
                "insight": c.default_negative_space + 0.05,
                "conflict": c.conflict_negative_space,
                "escalation": c.conflict_negative_space - 0.02,
                "release": c.default_negative_space + 0.08,
                "vision": c.default_negative_space + 0.15,
                "recap": c.default_negative_space,
                "call_to_action": c.cta_negative_space,
                "breathing_page": c.default_negative_space + 0.2,
            },
            "asymmetry": {
                "hook": "symmetric",
                "context": c.default_asymmetry,
                "evidence": "left_weighted" if c.default_asymmetry != "symmetric" else "balanced",
                "insight": "dynamic_shift",
                "conflict": "unbalanced",
                "escalation": "unbalanced",
                "release": "balanced",
                "vision": "symmetric",
                "recap": "balanced",
                "call_to_action": "symmetric",
                "breathing_page": "symmetric",
            },
        }

        if c.role_layer_overrides:
            # Layer overrides are stored for the resolver
            system["depth_layers"] = {"default": c.depth_layers_default}
            system["depth_layers"].update(c.role_layer_overrides)

        return system

    def _build_motion_language(self, m: MotionProfile) -> dict:
        system = {
            "default_easing": m.default_easing,
            "emphatic_easing": "cubic-bezier(0, 0.55, 0.45, 1)",
            "gentle_easing": "cubic-bezier(0.4, 0, 0.2, 1)",
            "snappy_easing": "cubic-bezier(0, 0, 0.2, 1)",
            "dramatic_easing": "cubic-bezier(0.2, 0, 1, 1)",
            "intensity_speed": {
                "1": {"duration_mult": m.speed_slow * 0.8, "stagger_mult": m.speed_slow},
                "2": {"duration_mult": m.speed_slow * 0.6, "stagger_mult": m.speed_slow * 0.7},
                "3": {"duration_mult": m.speed_moderate * 0.6, "stagger_mult": m.speed_moderate * 0.7},
                "4": {"duration_mult": m.speed_fast * 0.8, "stagger_mult": m.speed_fast},
                "5": {"duration_mult": m.speed_fast * 0.5, "stagger_mult": m.speed_fast * 0.6},
            },
        }

        if m.emotional_entrance_overrides:
            system["emotional_entrance"] = m.emotional_entrance_overrides

        return system

    def _build_transition_language(self, m: MotionProfile) -> dict:
        return {
            "default_transition": m.transition_default_type,
            "default_duration_ms": m.transition_default_duration,
            "default_easing": m.default_easing,
            "relation_transitions": {
                "progression": {"type": m.transition_default_type, "duration_ms": m.transition_default_duration, "easing": m.default_easing},
                "contrast": {"type": "hard_cut", "duration_ms": 150, "easing": "step-end"},
                "escalation": {"type": "intensify", "duration_ms": int(m.transition_default_duration * 0.6), "easing": "cubic-bezier(0.2, 0, 1, 1)"},
                "pivot": {"type": "swing_pivot", "duration_ms": int(m.transition_default_duration * 1.4), "easing": "cubic-bezier(0.5, 0, 0.3, 1)"},
                "emotional_shift": {"type": "color_shift", "duration_ms": int(m.transition_default_duration * 1.2), "easing": "cubic-bezier(0.35, 0, 0.1, 1)"},
            },
        }

    def _build_surface_system(self, s: SurfaceProfile, c: ColorProfile) -> dict:
        system = {}

        # Surface role overrides
        if s.surface_overrides:
            system["surfaces"] = s.surface_overrides

        # Background CSS
        backgrounds = {
            "brand_gradient": f"linear-gradient(135deg, {c.primary} 0%, {c.primary_light} 100%)",
            "brand_solid": c.primary,
            "dark_gradient": f"linear-gradient(170deg, {c.surface_dark} 0%, {c.surface_mid} 40%, {c.primary_dark} 100%)",
            "tension_gradient": f"linear-gradient(160deg, {c.surface_dark} 0%, {c.surface_mid} 50%, {c.primary_dark} 100%)",
            "horizon_gradient": f"linear-gradient(180deg, {c.surface_bg} 0%, color-mix(in srgb, {c.accent} 8%, {c.surface_bg}) 50%, color-mix(in srgb, {c.primary} 5%, {c.surface_bg}) 100%)",
            "soft_gradient": f"linear-gradient(180deg, {c.surface_bg} 0%, {c.surface_neutral} 100%)",
            "accent_wash": f"linear-gradient(135deg, {c.surface_bg} 0%, color-mix(in srgb, {c.accent} 12%, {c.surface_bg}) 100%)",
            "surface_bg": c.surface_bg,
            "surface_neutral": c.surface_neutral,
            "subtle_gradient": f"color-mix(in srgb, {c.surface_neutral} 50%, {c.surface_bg})",
        }

        if s.background_overrides:
            backgrounds.update(s.background_overrides)

        system["background_css"] = backgrounds

        return system

    def _build_spacing_system(self, sem: NormalizedAestheticSemantics) -> dict:
        ws = sem.composition.default_negative_space
        return {
            "unit_px": sem.spacing_unit,
            "slide_padding_v": f"{max(3, int(ws * 15))}vh",
            "slide_padding_h": f"{max(3, int(ws * 12))}vw",
            "content_gap": "0.5em",
            "title_margin_bottom": "0.3em",
            "subtitle_margin_bottom": "1em",
        }

    def _build_density_system(self, sem: NormalizedAestheticSemantics) -> dict:
        base = {
            "levels": {
                "1": {"max_points": 2, "max_chars_per_point": 40, "max_total_chars": 50},
                "2": {"max_points": 3, "max_chars_per_point": 60, "max_total_chars": 120},
                "3": {"max_points": 4, "max_chars_per_point": 80, "max_total_chars": 200},
                "4": {"max_points": 5, "max_chars_per_point": 90, "max_total_chars": 300},
                "5": {"max_points": 7, "max_chars_per_point": 100, "max_total_chars": 400},
            }
        }
        if sem.density_overrides:
            base["levels"].update(sem.density_overrides)
        return base

    def _build_emphasis_system(self, sem: NormalizedAestheticSemantics) -> dict:
        return {}  # Use defaults from schema; overrides only if needed

    def _build_cinematic_rhythm(self, sem: NormalizedAestheticSemantics) -> dict:
        return sem.rhythm_overrides if sem.rhythm_overrides else {}

    def _build_emotional_mapping(self, sem: NormalizedAestheticSemantics) -> dict:
        if sem.emotional_overrides:
            return {"kinetic_typography": sem.emotional_overrides}
        return {}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _hex_to_rgb_str(self, hex_color: str) -> str:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f"{r},{g},{b}"
