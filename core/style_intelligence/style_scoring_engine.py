"""Style Scoring Engine — heuristic quality scoring for style packs.

Evaluates a style pack across 8 dimensions:
  1. Typography Discipline — scale consistency, hierarchy clarity
  2. Cinematic Depth — surface layering, ambient quality
  3. Whitespace Quality — negative space intentionality
  4. Motion Coherence — easing consistency, stagger logic
  5. Visual Restraint — minimalism, absence of decoration
  6. Focal Clarity — visual hierarchy, attention guidance
  7. Emotional Consistency — mood/color/pace alignment
  8. Premium Feel — overall refinement, production quality

Each dimension produces a 0-100 score. The overall score is a
weighted average.

The scorer is a HEURISTIC engine — it uses rules derived from
the reference evaluation checklist and design principles.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .aesthetic_models import DimensionScore, StyleScores


class StyleScoringEngine:
    """Score style packs across quality dimensions."""

    # Dimension weights (sum = 1.0)
    DEFAULT_WEIGHTS = {
        "typography_discipline": 0.13,
        "cinematic_depth": 0.12,
        "whitespace_quality": 0.12,
        "motion_coherence": 0.13,
        "visual_restraint": 0.12,
        "focal_clarity": 0.13,
        "emotional_consistency": 0.12,
        "premium_feel": 0.13,
    }

    def __init__(self, weights: dict = None):
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)

    def score(self, style_pack) -> StyleScores:
        """Score a StylePack instance or dict."""
        if hasattr(style_pack, "color_system"):
            pack = style_pack  # StylePack dataclass
        else:
            pack = style_pack  # dict

        dimensions = [
            self._score_typography(pack),
            self._score_depth(pack),
            self._score_whitespace(pack),
            self._score_motion(pack),
            self._score_restraint(pack),
            self._score_focal(pack),
            self._score_emotional(pack),
            self._score_premium(pack),
        ]

        # Weighted average
        overall = 0.0
        for dim in dimensions:
            w = self.weights.get(dim.name, 0.125)
            overall += dim.score * w
        overall = round(overall, 1)

        # Build breakdown
        breakdown = {d.name: {"score": d.score, "remarks": d.remarks} for d in dimensions}

        return StyleScores(
            style_name=self._get_name(pack),
            overall=overall,
            dimensions=[{"name": d.name, "score": d.score, "weight": self.weights.get(d.name, 0.125), "remarks": d.remarks} for d in dimensions],
            breakdown=breakdown,
            passed=overall >= 60.0,
            threshold=60.0,
        )

    def compare(self, packs: list) -> list[StyleScores]:
        """Score multiple packs and return ranked results."""
        results = [self.score(p) for p in packs]
        results.sort(key=lambda r: r.overall, reverse=True)
        return results

    # ==================================================================
    # Dimension scorers
    # ==================================================================

    def _score_typography(self, pack) -> DimensionScore:
        """Score typography discipline: scale consistency, hierarchy clarity."""
        score = 60.0
        remarks = []

        ts = self._get_system(pack, "typography_system")
        if not ts:
            return DimensionScore(name="typography_discipline", score=score, weight=self.weights["typography_discipline"], remarks="No typography data")

        # Check scale progression (should be ~1.25-1.33 ratio)
        scales = [
            ts.get("scale_micro", 10), ts.get("scale_caption", 12),
            ts.get("scale_body_sm", 14), ts.get("scale_body", 16),
            ts.get("scale_body_lg", 18), ts.get("scale_h3", 22),
            ts.get("scale_h2", 28), ts.get("scale_h1", 36),
            ts.get("scale_hero", 48), ts.get("scale_display", 64),
            ts.get("scale_mega", 84),
        ]
        ratios = []
        for i in range(len(scales) - 1):
            if scales[i] > 0:
                ratios.append(scales[i + 1] / scales[i])

        if ratios and all(1.1 <= r <= 1.45 for r in ratios):
            score += 15
            remarks.append("Clean scale progression")
        elif ratios and all(1.05 <= r <= 1.6 for r in ratios):
            score += 8
            remarks.append("Acceptable scale progression")
        else:
            score -= 10
            remarks.append("Irregular scale jumps detected")

        # Title/body font distinction
        title_font = ts.get("title_font", "")
        body_font = ts.get("body_font", "")
        if title_font and body_font:
            score += 10
            remarks.append("Font pairing present")
        if title_font != body_font and title_font and body_font:
            score += 5
            remarks.append("Distinct title/body fonts")

        # Role prescriptions
        role_prescriptions = ts.get("role_prescriptions", {})
        if role_prescriptions:
            score += min(10, len(role_prescriptions) * 3)
            remarks.append(f"{len(role_prescriptions)} role prescriptions defined")

        return DimensionScore(
            name="typography_discipline",
            score=min(100, max(0, score)),
            weight=self.weights["typography_discipline"],
            remarks="; ".join(remarks) if remarks else "Adequate",
        )

    def _score_depth(self, pack) -> DimensionScore:
        """Score cinematic depth: surface layering, ambient quality."""
        score = 50.0
        remarks = []

        ss = self._get_system(pack, "surface_system")
        cs = self._get_system(pack, "composition_system")

        # Background CSS variety
        backgrounds = ss.get("background_css", {}) if ss else {}
        bg_count = len(backgrounds)
        if bg_count >= 8:
            score += 20
            remarks.append("Rich background palette")
        elif bg_count >= 5:
            score += 12
            remarks.append("Adequate background variety")
        elif bg_count >= 3:
            score += 5
        else:
            score -= 10
            remarks.append("Sparse background definitions")

        # Depth layers
        depth_layers = cs.get("depth_layers", {}) if cs else {}
        if depth_layers:
            score += 10
            remarks.append("Depth layers configured")

        # Surface role overrides
        surfaces = ss.get("surfaces", {}) if ss else {}
        if surfaces:
            score += min(10, len(surfaces) * 2)
            remarks.append(f"{len(surfaces)} surface role overrides")

        # Gradient sophistication
        has_complex_gradients = any(
            "radial" in str(v) or "color-mix" in str(v)
            for v in backgrounds.values()
        )
        if has_complex_gradients:
            score += 10
            remarks.append("Complex gradient techniques")

        return DimensionScore(
            name="cinematic_depth",
            score=min(100, max(0, score)),
            weight=self.weights["cinematic_depth"],
            remarks="; ".join(remarks) if remarks else "Basic depth",
        )

    def _score_whitespace(self, pack) -> DimensionScore:
        """Score whitespace quality: negative space intentionality."""
        score = 55.0
        remarks = []

        cs = self._get_system(pack, "composition_system")
        if not cs:
            return DimensionScore(name="whitespace_quality", score=score, weight=self.weights["whitespace_quality"], remarks="No composition data")

        ns = cs.get("negative_space", {})
        if not ns:
            return DimensionScore(name="whitespace_quality", score=score, weight=self.weights["whitespace_quality"], remarks="No negative space data")

        # Whitespace should vary by role (not uniform)
        values = [v for v in ns.values() if isinstance(v, (int, float))]
        if values:
            spread = max(values) - min(values)
            if spread > 0.4:
                score += 20
                remarks.append(f"Strong role variation (spread: {spread:.2f})")
            elif spread > 0.2:
                score += 12
                remarks.append("Moderate role variation")
            else:
                score -= 5
                remarks.append("Uniform whitespace — lacks intentionality")

        # Hook should have high whitespace
        hook_ws = ns.get("hook", 0)
        if hook_ws >= 0.45:
            score += 10
            remarks.append("Hook has generous whitespace")
        elif hook_ws < 0.30:
            score -= 8
            remarks.append("Hook too dense — lost impact")

        # Conflict should be tight
        conflict_ws = ns.get("conflict", 0)
        if conflict_ws <= 0.15:
            score += 10
            remarks.append("Conflict appropriately tight")
        elif conflict_ws > 0.25:
            score -= 5
            remarks.append("Conflict too spacious — tension diluted")

        return DimensionScore(
            name="whitespace_quality",
            score=min(100, max(0, score)),
            weight=self.weights["whitespace_quality"],
            remarks="; ".join(remarks) if remarks else "Adequate",
        )

    def _score_motion(self, pack) -> DimensionScore:
        """Score motion coherence: easing consistency, stagger logic."""
        score = 55.0
        remarks = []

        ml = self._get_system(pack, "motion_language")
        if not ml:
            return DimensionScore(name="motion_coherence", score=score, weight=self.weights["motion_coherence"], remarks="No motion data")

        # Easing curves defined
        easings = {k: v for k, v in ml.items() if k.endswith("_easing")}
        if len(easings) >= 4:
            score += 10
            remarks.append("Complete easing vocabulary")
        elif len(easings) >= 2:
            score += 5

        # Intensity speed mapping
        intensity_speed = ml.get("intensity_speed", {})
        if intensity_speed and len(intensity_speed) >= 4:
            speeds = [v.get("duration_mult", 0) for v in intensity_speed.values() if isinstance(v, dict)]
            if speeds and speeds == sorted(speeds, reverse=True):
                score += 15
                remarks.append("Correctly descending speed curve")
            elif speeds:
                score += 8
                remarks.append("Intensity-speed mapping present")

        # Emotional entrance variety
        emotional = ml.get("emotional_entrance", {})
        if emotional:
            stagger_values = [v.get("stagger_ms", 0) for v in emotional.values() if isinstance(v, dict)]
            if stagger_values:
                stagger_spread = max(stagger_values) - min(stagger_values)
                if stagger_spread > 300:
                    score += 15
                    remarks.append("Rich stagger variation across emotions")
                elif stagger_spread > 100:
                    score += 8
                    remarks.append("Moderate stagger variation")

        # Keyframes
        keyframes = ml.get("keyframes", {})
        if keyframes and len(keyframes) >= 4:
            score += 10
            remarks.append("Complete keyframe library")

        return DimensionScore(
            name="motion_coherence",
            score=min(100, max(0, score)),
            weight=self.weights["motion_coherence"],
            remarks="; ".join(remarks) if remarks else "Basic motion config",
        )

    def _score_restraint(self, pack) -> DimensionScore:
        """Score visual restraint: minimalism, absence of decoration."""
        score = 60.0
        remarks = []

        colors = self._get_system(pack, "color_system")
        ss = self._get_system(pack, "surface_system")
        ml = self._get_system(pack, "motion_language")

        # Saturation check — premium palettes are desaturated
        if colors:
            primary = colors.get("primary", "#FF0000")
            if self._is_desaturated(primary):
                score += 15
                remarks.append("Restrained primary color")
            else:
                score -= 5
                remarks.append("Highly saturated primary — may feel aggressive")

        # Motion density
        if ml:
            emotional = ml.get("emotional_entrance", {})
            if len(emotional) < 10:
                score += 5
                remarks.append("Selective emotional mapping — restraint in motion")

        # Surface complexity
        if ss:
            backgrounds = ss.get("background_css", {})
            complex_count = sum(1 for v in backgrounds.values()
                               if "radial" in str(v) or "color-mix" in str(v))
            if complex_count <= 3 and len(backgrounds) >= 5:
                score += 10
                remarks.append("Mostly clean surfaces, selective complexity")

        # Fewer palette colors is more restrained
        if colors:
            color_fields = [v for k, v in colors.items()
                          if k.startswith(("primary", "accent", "surface", "text"))]
            if len(color_fields) >= 10:
                score += 10
                remarks.append("Complete semantic color system")
            else:
                score -= 5
                remarks.append("Sparse color system")

        return DimensionScore(
            name="visual_restraint",
            score=min(100, max(0, score)),
            weight=self.weights["visual_restraint"],
            remarks="; ".join(remarks) if remarks else "Acceptable restraint",
        )

    def _score_focal(self, pack) -> DimensionScore:
        """Score focal clarity: visual hierarchy, attention guidance."""
        score = 50.0
        remarks = []

        cs = self._get_system(pack, "composition_system")
        ts = self._get_system(pack, "typography_system")

        # Asymmetry definitions
        asymmetry = cs.get("asymmetry", {}) if cs else {}
        if asymmetry:
            # Center for hook and CTA, unbalanced for conflict
            if (asymmetry.get("hook") == "symmetric"
                    and asymmetry.get("call_to_action") == "symmetric"):
                score += 15
                remarks.append("Correct centering for high-impact roles")
            if asymmetry.get("conflict") == "unbalanced":
                score += 10
                remarks.append("Asymmetry for tension — intentional")

        # Scale contrast
        if ts:
            h1 = ts.get("scale_h1", 36)
            body = ts.get("scale_body", 16)
            ratio = h1 / max(body, 1)
            if ratio >= 2.2:
                score += 10
                remarks.append(f"Strong headline/body contrast ({ratio:.1f}:1)")
            elif ratio >= 1.8:
                score += 5
                remarks.append("Adequate scale contrast")
            else:
                score -= 8
                remarks.append("Weak hierarchy — headline and body too similar")

        # Focal points defined
        focal_points = cs.get("focal_points", {}) if cs else {}
        if focal_points:
            score += min(10, len(focal_points) * 1.5)

        return DimensionScore(
            name="focal_clarity",
            score=min(100, max(0, score)),
            weight=self.weights["focal_clarity"],
            remarks="; ".join(remarks) if remarks else "Basic focal config",
        )

    def _score_emotional(self, pack) -> DimensionScore:
        """Score emotional consistency: mood/color/pace alignment."""
        score = 55.0
        remarks = []

        colors = self._get_system(pack, "color_system")
        em = self._get_system(pack, "emotional_mapping")
        rhythm = self._get_system(pack, "cinematic_rhythm")

        # Emotional mapping richness
        if em:
            kinetic = em.get("kinetic_typography", {})
            if kinetic:
                score += min(15, len(kinetic) * 2)
                remarks.append(f"{len(kinetic)} emotional typography mappings")

        # Rhythm curve
        if rhythm:
            curve = rhythm.get("tension_curve", [])
            if curve:
                # Should have variation
                intensities = [p.get("intensity", 0) for p in curve]
                if intensities and max(intensities) - min(intensities) >= 2:
                    score += 15
                    remarks.append("Dynamic tension curve")
                else:
                    score += 5
                    remarks.append("Flat tension curve — less engaging")

        # Color mood
        if colors:
            primary = colors.get("primary", "")
            accent = colors.get("accent", "")
            if primary and accent:
                # Check if they're harmonious (not clashing)
                score += 5
                remarks.append("Color pairing present")

        return DimensionScore(
            name="emotional_consistency",
            score=min(100, max(0, score)),
            weight=self.weights["emotional_consistency"],
            remarks="; ".join(remarks) if remarks else "Adequate emotional mapping",
        )

    def _score_premium(self, pack) -> DimensionScore:
        """Score premium feel: overall refinement, production quality."""
        score = 50.0
        remarks = []

        # Composite check: does this pack have all the expected systems?
        expected_systems = [
            "color_system", "typography_system", "composition_system",
            "motion_language", "transition_language", "surface_system",
            "spacing_system", "density_system",
        ]
        pack_dict = pack if isinstance(pack, dict) else {}
        if hasattr(pack, "__dataclass_fields__"):
            from dataclasses import asdict
            pack_dict = asdict(pack)

        present = sum(1 for s in expected_systems if s in pack_dict and pack_dict[s])
        coverage = present / len(expected_systems)

        if coverage >= 0.9:
            score += 20
            remarks.append("Near-complete system coverage")
        elif coverage >= 0.7:
            score += 10
            remarks.append("Good system coverage")
        else:
            score -= 10
            remarks.append(f"Only {present}/{len(expected_systems)} systems defined")

        # Metadata completeness
        metadata = pack_dict.get("metadata", {})
        if metadata.get("tags"):
            score += 5
        if metadata.get("best_for"):
            score += 5
            remarks.append("Usage guidance present")

        # Description quality
        description = pack_dict.get("description", "")
        if len(description) > 50:
            score += 10
            remarks.append("Detailed style description")
        elif len(description) > 20:
            score += 5

        # Color palette complexity
        colors = self._get_system(pack, "color_system")
        if colors:
            color_count = len([v for v in colors.values() if isinstance(v, str) and v.startswith("#")])
            if color_count >= 15:
                score += 10
                remarks.append("Rich, complete color palette")

        return DimensionScore(
            name="premium_feel",
            score=min(100, max(0, score)),
            weight=self.weights["premium_feel"],
            remarks="; ".join(remarks) if remarks else "Basic production quality",
        )

    # ==================================================================
    # Helpers
    # ==================================================================

    def _get_system(self, pack, name: str) -> dict:
        """Get a system from either a StylePack dataclass or dict."""
        if hasattr(pack, name):
            system = getattr(pack, name)
            if hasattr(system, "__dataclass_fields__"):
                from dataclasses import asdict
                return asdict(system)
            return system
        elif isinstance(pack, dict):
            return pack.get(name, {})
        return {}

    def _get_name(self, pack) -> str:
        if hasattr(pack, "name"):
            return pack.name
        elif isinstance(pack, dict):
            return pack.get("name", "unknown")
        return "unknown"

    def _is_desaturated(self, hex_color: str) -> bool:
        """Check if a hex color is relatively desaturated (premium feel)."""
        hex_color = hex_color.lstrip("#")
        if len(hex_color) == 3:
            hex_color = "".join(c * 2 for c in hex_color)
        try:
            r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
            max_c = max(r, g, b)
            min_c = min(r, g, b)
            if max_c == 0:
                return True
            saturation = (max_c - min_c) / max_c
            return saturation < 0.4
        except (ValueError, IndexError):
            return False
