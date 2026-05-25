"""Family Pipeline — per-family orchestration of the full style intelligence pipeline.

Operates entirely within the bounds of a single style family:
  References → Extract → Parse → Generate → Score → Benchmark

All outputs are stored within the family directory:
  family/
    references/raw, selected, distilled/
    analysis/extracted_observations.json
    analysis/parsed_semantics.json
    analysis/scoring_report.json
    <pack>/style.json
    outputs/benchmark.html
    outputs/runtime_demo.html
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from ..style_system.family_manager import FamilyManager
from ..style_system.family_isolation import FamilyIsolation, isolation_report
from ..style_system.style_pack_loader import StylePackLoader
from .style_extractor import StyleExtractor
from .aesthetic_parser import AestheticParser
from .style_pack_generator import StylePackGenerator
from .style_scoring_engine import StyleScoringEngine
from .aesthetic_models import NormalizedAestheticSemantics


class FamilyPipeline:
    """Orchestrate the full style intelligence pipeline within a family."""

    def __init__(self, family_name: str, styles_root: str = None):
        if styles_root is None:
            styles_root = os.path.join(
                os.path.dirname(__file__), "..", "styles"
            )
        self.styles_root = os.path.abspath(styles_root)
        self.family_name = family_name
        self.family_dir = os.path.join(self.styles_root, family_name)

        if not os.path.isdir(self.family_dir):
            raise FileNotFoundError(f"Family not found: {family_name}")

        self._family_mgr = FamilyManager(styles_root)
        self._manifest = self._family_mgr.get_manifest(family_name)

        # Pipeline stages
        self._extractor = StyleExtractor()
        self._parser = AestheticParser()
        self._generator = StylePackGenerator(styles_root)
        self._scorer = StyleScoringEngine()
        self._loader = StylePackLoader(styles_root)
        self._isolation = FamilyIsolation()

    # ------------------------------------------------------------------
    # Full pipeline: reference → scored style pack
    # ------------------------------------------------------------------

    def run(self, reference: dict, pack_name: str = None,
            inherits: str = None) -> dict:
        """Run the complete pipeline for a single reference.

        Args:
            reference: Distillation dict or observation dict
            pack_name: Name for the generated pack (auto-derived if None)
            inherits: Parent pack name within the same family (or None)

        Returns:
            Dict with all pipeline artifacts
        """
        print(f"\n{'=' * 60}")
        print(f"  Family Pipeline: {self.family_name}")
        print(f"  Philosophy: {self._manifest.philosophy[:80]}...")
        print(f"{'=' * 60}")

        # Stage 1: Extract
        print("\n[1/6] Extracting aesthetic observations...")
        observations = self._extractor.extract_from_distillation(reference)
        print(f"  Brand: {observations.brand}")
        print(f"  Typography: {observations.typography.font_character}")
        print(f"  Motion: {observations.motion.easing_philosophy}")
        print(f"  Whitespace: {observations.spacing.whitespace_ratio}")
        print(f"  Confidence: {observations.extractor_confidence:.0%}")

        # Stage 2: Parse
        print("\n[2/6] Parsing into normalized semantics...")
        semantics = self._parser.parse(observations)
        print(f"  Style name: {semantics.style_name}")
        print(f"  Tags: {semantics.metadata_tags}")

        # Override pack name if specified
        if pack_name:
            semantics.style_name = pack_name

        # Set inheritance within family
        if inherits:
            # Ensure inheritance stays within family
            if "/" in inherits:
                parent_family = inherits.split("/")[0]
                if parent_family != self.family_name:
                    raise ValueError(
                        f"Cross-family inheritance forbidden: {inherits} "
                        f"is not in family '{self.family_name}'"
                    )
            semantics.inherits = inherits

        # Stage 3: Generate
        print("\n[3/6] Generating style pack...")
        pack_dict = self._generator.generate(semantics)

        # Validate against family manifest
        violations = self._family_mgr.validate_pack_against_family(
            pack_dict, self.family_name
        )
        if violations:
            print(f"  WARNING: {len(violations)} family violations found:")
            for v in violations:
                print(f"    - {v}")

        pack_path = self._generator.generate_and_save(semantics, family=self.family_name)
        print(f"  Saved: {pack_path}")

        # Verify it loads
        qualified_name = f"{self.family_name}/{semantics.style_name}"
        pack = self._loader.load(qualified_name)
        print(f"  Verified: {pack.name} (color={bool(pack.color_system.primary)})")

        # Stage 4: Score
        print("\n[4/6] Scoring style pack...")
        scores = self._scorer.score(pack)
        print(f"  Overall: {scores.overall}/100 {'PASS' if scores.passed else 'FAIL'}")
        for dim in scores.dimensions:
            print(f"    {dim['name']}: {dim['score']:.0f}")

        # Stage 5: Render demo
        print("\n[5/6] Rendering demo...")
        demo_state = self._create_demo_state()
        demo_path = self._render_demo(demo_state, qualified_name)

        # Stage 6: Save analysis artifacts
        print("\n[6/6] Saving analysis artifacts...")
        self._save_analysis(observations, semantics, scores, qualified_name)

        # Check isolation
        families = self._family_mgr.discover_families()
        violations = self._isolation.validate_all(self.styles_root, families)
        print(f"\n  Isolation check: {isolation_report(violations)}")

        return {
            "family": self.family_name,
            "pack_name": semantics.style_name,
            "qualified_name": qualified_name,
            "pack_path": pack_path,
            "demo_path": demo_path,
            "scores": {"overall": scores.overall, "passed": scores.passed,
                        "dimensions": scores.dimensions},
            "confidence": observations.extractor_confidence,
        }

    # ------------------------------------------------------------------
    # Save/Load analysis artifacts
    # ------------------------------------------------------------------

    def _save_analysis(self, observations, semantics,
                        scores, qualified_name: str):
        """Save pipeline intermediate artifacts to family/analysis/."""
        analysis_dir = os.path.join(self.family_dir, "analysis")
        os.makedirs(analysis_dir, exist_ok=True)

        # Observations
        from dataclasses import asdict
        obs_dict = asdict(observations)
        obs_dict["pipeline_run_at"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        with open(os.path.join(analysis_dir, "extracted_observations.json"),
                  "w", encoding="utf-8") as f:
            json.dump(obs_dict, f, indent=2, ensure_ascii=False, default=str)

        # Semantics
        sem_dict = asdict(semantics)
        sem_dict["pipeline_run_at"] = datetime.now(timezone.utc).strftime(
            "%Y-%m-%dT%H:%M:%SZ")
        with open(os.path.join(analysis_dir, "parsed_semantics.json"),
                  "w", encoding="utf-8") as f:
            json.dump(sem_dict, f, indent=2, ensure_ascii=False, default=str)

        # Scoring report
        report = {
            "family": self.family_name,
            "pack": qualified_name,
            "scored_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "overall": scores.overall,
            "passed": scores.passed,
            "dimensions": scores.dimensions,
            "breakdown": scores.breakdown,
        }
        with open(os.path.join(analysis_dir, "scoring_report.json"),
                  "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"  Saved to {analysis_dir}/")

    # ------------------------------------------------------------------
    # Demo rendering
    # ------------------------------------------------------------------

    def _render_demo(self, state: dict, qualified_name: str) -> str:
        """Render a demo HTML for the generated pack."""
        from ..rendering import render_to_file

        output_dir = os.path.join(self.family_dir, "outputs")
        os.makedirs(output_dir, exist_ok=True)

        pack_name = qualified_name.replace("/", "_")
        path = os.path.join(output_dir, f"runtime_demo_{pack_name}.html")
        render_to_file(state, path, style_pack_name=qualified_name)
        size_kb = os.path.getsize(path) / 1024
        print(f"  Rendered: {path} ({size_kb:.1f} KB)")
        return path

    def _create_demo_state(self) -> dict:
        """Create a minimal representative presentation state."""
        return {
            "meta": {
                "title": f"Style Demo — {self.family_name}",
                "style": "cinematic",
                "uuid": f"demo_{self.family_name}",
                "version": "0.1.0",
                "language": "zh-CN",
            },
            "context": {
                "audience": {"profile": "技术决策者", "knowledge_level": "advanced"},
                "occasion": {"type": "tech_conference", "formality": "semi_formal"},
                "intent": {"primary_goal": "persuade"},
                "duration": {"total_minutes": 12},
            },
            "narrative_arc": {
                "sections": [
                    {"id": "s1", "label": "Opening", "slide_range": [0, 0], "function": "hook"},
                    {"id": "s2", "label": "Build", "slide_range": [1, 2], "function": "evidence"},
                    {"id": "s3", "label": "Climax", "slide_range": [3, 3], "function": "insight"},
                    {"id": "s4", "label": "Close", "slide_range": [4, 4], "function": "call_to_action"},
                ],
            },
            "slides": [
                {
                    "index": 0, "id": "s0", "narrative_role": "hook",
                    "emotional_role": "curious", "structural_role": "cover",
                    "title": "The Future Is Written in Motion",
                    "subtitle": "A cinematic exploration of what's possible",
                    "content": {
                        "lead": "When presentation becomes experience, information becomes understanding.",
                        "points": ["Motion that means something", "Space that breathes", "Typography that commands"],
                        "visual_description": "Dark gradient with single point of light expanding",
                    },
                    "rhythm": {"intensity": 3, "pace": "moderate"},
                    "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                    "relation_to_next": "progression",
                },
                {
                    "index": 1, "id": "s1", "narrative_role": "context",
                    "emotional_role": "engaged", "structural_role": "overview",
                    "title": "The Landscape",
                    "subtitle": "Where we stand today",
                    "content": {
                        "lead": "Three forces are converging to redefine how we communicate.",
                        "points": ["AI-native tools are reshaping the creation pipeline",
                                   "Audiences expect cinema, not slides",
                                   "The gap between capable and compelling is widening"],
                    },
                    "rhythm": {"intensity": 2, "pace": "slow"},
                    "design": {"layout_mode": "grid", "emphasis_level": "normal"},
                    "relation_to_next": "deepening",
                },
                {
                    "index": 2, "id": "s2", "narrative_role": "evidence",
                    "emotional_role": "confident", "structural_role": "evidence",
                    "title": "The Numbers",
                    "subtitle": "Precision creates trust",
                    "content": {
                        "lead": "Data doesn't lie. The evidence for cinematic communication is overwhelming.",
                        "points": ["83% higher retention with motion-guided narrative",
                                   "2.4x engagement lift from spatial continuity",
                                   "67% of executives prefer non-linear presentations"],
                        "data": {"type": "chart", "headline": "Audience Engagement Metrics 2024-2026"},
                    },
                    "rhythm": {"intensity": 3, "pace": "moderate"},
                    "design": {"layout_mode": "split", "emphasis_level": "normal"},
                    "relation_to_next": "escalation",
                },
                {
                    "index": 3, "id": "s3", "narrative_role": "insight",
                    "emotional_role": "surprised", "structural_role": "insight",
                    "title": "The Hidden Truth",
                    "subtitle": "What everyone is missing",
                    "content": {
                        "lead": "The best presentation isn't the one with the most animations. It's the one where every frame earns its place.",
                        "points": ["Restraint is the highest form of confidence",
                                   "Negative space isn't empty — it's loaded",
                                   "Motion without meaning is just noise"],
                    },
                    "rhythm": {"intensity": 4, "pace": "moderate"},
                    "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                    "relation_to_next": "emotional_shift",
                },
                {
                    "index": 4, "id": "s4", "narrative_role": "call_to_action",
                    "emotional_role": "inspired", "structural_role": "cta",
                    "title": "Build What Matters",
                    "subtitle": "The tools exist. The question is what you'll do with them.",
                    "content": {
                        "lead": "Every presentation is a choice. Choose cinema.",
                        "points": ["Master motion. Master meaning. Master attention."],
                    },
                    "rhythm": {"intensity": 5, "pace": "slow"},
                    "design": {"layout_mode": "centered", "emphasis_level": "hero"},
                    "relation_to_next": "",
                },
            ],
            "design_system": {
                "palette": {"colors": {}},
                "typography": {"title_font": "system-ui", "body_font": "system-ui", "scale": []},
                "spacing_unit": 8, "corner_style": "rounded", "grid_columns": 12,
            },
            "runtime": {"generation_stage": "demo", "pipeline_version": "P5.5-Family"},
        }
