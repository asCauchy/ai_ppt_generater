"""P5.5 Style Intelligence Pipeline — End-to-End Verification.

Demonstrates the complete pipeline:
  Reference distillation → Extract → Parse → Generate → Score → Benchmark

Also scores existing style packs and runs the benchmark renderer.
"""

import json
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, ROOT)

from core.style_intelligence.style_extractor import StyleExtractor
from core.style_intelligence.aesthetic_parser import AestheticParser
from core.style_intelligence.style_pack_generator import StylePackGenerator
from core.style_intelligence.style_scoring_engine import StyleScoringEngine
from core.style_intelligence.benchmark_renderer import BenchmarkRenderer
from core.style_system.style_pack_loader import StylePackLoader
from tools.generate_style_demos import create_demo_state


def simulate_apple_reference():
    """Simulate a filled distillation template for an Apple keynote reference."""
    return {
        "source": "Apple WWDC 2024 Keynote Opening",
        "brand": "Apple",
        "evaluation_score": 46,
        "easing_philosophy": "ease-out dominant, very slow deceleration — elements glide into place",
        "stagger_pattern": "sequential, 200ms stagger between elements",
        "speed_range": "slow and deliberate, holds at peak for breathing room",
        "motion_grammar": {
            "easing": "ease-out",
            "stagger": "sequential",
            "speed": "slow",
            "scale_variation": 0,
            "techniques": "masked reveals, opacity fades paired with 20px vertical drift",
        },
        "transition_type": {
            "primary": "dissolve",
            "spatial": "next scene feels like same canvas, zoom-in continuity",
            "purpose": "maintain flow — never jar the viewer",
        },
        "composition_pattern": {
            "focal_point": "absolute center, single hero element",
            "grid_structure": "symmetrical, centered",
            "depth_layers": 2,
            "element_count": "few(4-6)",
            "background_treatment": "atmospheric",
            "negative_space": "generous — 50%+ empty",
        },
        "typography_pattern": {
            "fonts": ["SF Pro Display", "SF Pro Text"],
            "font_character": "sans_geometric",
            "scale_range": "10px caption to 80px mega headline",
            "weight_contrast": "multi-weight system — Regular, Medium, Semibold, Bold, Heavy",
            "reveal_behavior": "full block fade-up, title first, then subtitle, then body",
            "alignment": "center",
        },
        "emotional_effect": {
            "primary_emotion": "confidence",
            "tension_profile": "gentle — calm opening, gradual build",
            "how": "Through vast negative space, slow pacing, deep blacks, single accent glow",
        },
        "surface": {
            "quality": "dark gradient, subtle noise texture",
            "depth": "shadow and ambient glow",
            "glass": False,
            "noise": True,
        },
    }


def simulate_stripe_reference():
    """Simulate a Stripe presentation reference."""
    return {
        "source": "Stripe Sessions 2024 Keynote",
        "brand": "Stripe",
        "evaluation_score": 42,
        "easing_philosophy": "spring-based, bouncy but controlled",
        "stagger_pattern": "wave, 100ms between elements",
        "speed_range": "moderate, snappy entrances",
        "motion_grammar": {
            "easing": "spring",
            "stagger": "wave",
            "speed": "moderate",
            "scale_variation": 1,
            "techniques": "scale-bounce, gradient shifts, morphing icons",
        },
        "transition_type": {
            "primary": "push",
            "spatial": "slides push left-to-right, maintaining directional flow",
            "purpose": "forward momentum — always moving right",
        },
        "composition_pattern": {
            "focal_point": "left-weighted with gradient visual on right",
            "grid_structure": "asymmetrical, split 60/40",
            "depth_layers": 3,
            "element_count": "moderate(7-10)",
            "background_treatment": "gradient",
            "negative_space": "moderate",
        },
        "typography_pattern": {
            "fonts": ["Stripe Sans", "Inter"],
            "font_character": "sans_humanist",
            "scale_range": "12px to 56px",
            "weight_contrast": "Regular to Bold, two-weight system",
            "reveal_behavior": "word-by-word stagger for headlines",
            "alignment": "left",
        },
        "emotional_effect": {
            "primary_emotion": "warmth",
            "tension_profile": "building — steady energy rise throughout",
            "how": "Warm gradient colors, bouncy motion, friendly typography, human imagery",
        },
        "surface": {
            "quality": "gradient with glass overlays",
            "depth": "layered with blur backgrounds",
            "glass": True,
            "noise": False,
        },
    }


def main():
    print("=" * 60)
    print("  P5.5 Style Intelligence Pipeline — E2E Verification")
    print("=" * 60)

    extractor = StyleExtractor()
    parser = AestheticParser()
    generator = StylePackGenerator()
    scorer = StyleScoringEngine()

    # ==================================================================
    # PART 1: Extract → Parse → Generate → Score (Apple reference)
    # ==================================================================
    print("\n" + "=" * 60)
    print("  PART 1: Reference → Style Pack Pipeline")
    print("=" * 60)

    apple_ref = simulate_apple_reference()
    print(f"\n[1/4] Extracting from: {apple_ref['source']}")
    apple_obs = extractor.extract_from_distillation(apple_ref)
    print(f"  Brand: {apple_obs.brand}")
    print(f"  Typography: {apple_obs.typography.font_character}, weight={apple_obs.typography.headline_weight}")
    print(f"  Color mood: {apple_obs.color.mood}, primary={apple_obs.color.primary_hex}")
    print(f"  Motion: {apple_obs.motion.easing_philosophy}, speed={apple_obs.motion.speed_range}")
    print(f"  Whitespace ratio: {apple_obs.spacing.whitespace_ratio}")
    print(f"  Emotional: {apple_obs.emotional.primary_mood}, tension={apple_obs.emotional.tension_profile}")
    print(f"  Confidence: {apple_obs.extractor_confidence:.0%}")

    print(f"\n[2/4] Parsing into normalized semantics...")
    apple_sem = parser.parse(apple_obs)
    print(f"  Style name: {apple_sem.style_name}")
    print(f"  Description: {apple_sem.style_description[:100]}...")
    print(f"  Title font: {apple_sem.typography.title_font}")
    print(f"  Scale mega: {apple_sem.typography.scale_mega}px")
    print(f"  Negative space: {apple_sem.composition.default_negative_space}")
    print(f"  Easing: {apple_sem.motion.default_easing}")
    print(f"  Tags: {apple_sem.metadata_tags}")
    print(f"  Confidence: {apple_sem.confidence:.0%}")

    print(f"\n[3/4] Generating style pack...")
    apple_pack_path = generator.generate_and_save(apple_sem)
    print(f"  Saved: {apple_pack_path}")
    # Verify it loads
    loader = StylePackLoader()
    apple_pack = loader.load(apple_sem.style_name)
    print(f"  Verified: {apple_pack.name} v{apple_pack.version}")
    print(f"  Systems: color={bool(apple_pack.color_system.primary)}, "
          f"typo={bool(apple_pack.typography_system.title_font)}, "
          f"motion={bool(apple_pack.motion_language.default_easing)}")

    print(f"\n[4/4] Scoring generated pack...")
    apple_scores = scorer.score(apple_pack)
    print(f"  Overall: {apple_scores.overall}/100 {'PASS' if apple_scores.passed else 'FAIL'}")
    for dim in apple_scores.dimensions:
        bar = "#" * int(dim["score"] / 10) + "-" * (10 - int(dim["score"] / 10))
        print(f"  {dim['name']:30s} [{bar}] {dim['score']:.0f}")

    # ==================================================================
    # PART 2: Same pipeline for Stripe reference
    # ==================================================================
    print("\n" + "=" * 60)
    print("  PART 2: Stripe Reference → Style Pack")
    print("=" * 60)

    stripe_ref = simulate_stripe_reference()
    stripe_obs = extractor.extract_from_distillation(stripe_ref)
    stripe_sem = parser.parse(stripe_obs)
    stripe_pack_path = generator.generate_and_save(stripe_sem)
    stripe_pack = loader.load(stripe_sem.style_name)
    stripe_scores = scorer.score(stripe_pack)
    print(f"\n  Style: {stripe_sem.style_name}")
    print(f"  Overall: {stripe_scores.overall}/100 {'PASS' if stripe_scores.passed else 'FAIL'}")

    # ==================================================================
    # PART 3: Score existing packs
    # ==================================================================
    print("\n" + "=" * 60)
    print("  PART 3: Score Existing Style Packs")
    print("=" * 60)

    for name in ["apple_minimal", "chinese_macro"]:
        pack = loader.load(name)
        scores = scorer.score(pack)
        print(f"\n  {name}: {scores.overall}/100 {'PASS' if scores.passed else 'FAIL'}")
        for dim in scores.dimensions:
            print(f"    {dim['name']:30s} {dim['score']:.0f}")

    # ==================================================================
    # PART 4: Benchmark Renderer
    # ==================================================================
    print("\n" + "=" * 60)
    print("  PART 4: Benchmark Renderer — Multi-Style Comparison")
    print("=" * 60)

    state = create_demo_state()
    benchmark = BenchmarkRenderer()
    report = benchmark.run(
        state,
        style_names=["apple_minimal", "chinese_macro",
                      apple_sem.style_name, stripe_sem.style_name],
        state_title="P5.5 Intelligence Pipeline Benchmark",
    )

    # ==================================================================
    # Summary
    # ==================================================================
    print("\n" + "=" * 60)
    print("  P5.5 VERIFICATION COMPLETE")
    print("=" * 60)
    print(f"\n  Generated style packs: {apple_sem.style_name}, {stripe_sem.style_name}")
    print(f"  Scored packs: 4")
    print(f"  Benchmark demos: {len(report.style_results)}")
    print(f"\n  Available style packs:")
    for name in loader.list_packs():
        pack = loader.load(name)
        scores = scorer.score(pack)
        print(f"    {name:30s} — {scores.overall:.0f}/100")

    print(f"\n  Outputs directory: {os.path.join(ROOT, 'outputs')}")
    print(f"  Style packs directory: {os.path.join(ROOT, 'core', 'styles')}")


if __name__ == "__main__":
    main()
