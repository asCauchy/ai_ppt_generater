"""State Mapper — Presentation State → SemanticRequirements.

This is the bridge between the presentation state and the style system.
It translates concrete state (narrative_role, emotional_role, intensity, rhythm...)
into SemanticRequirements — a style-agnostic description of WHAT the slide needs.

The style_resolver then takes SemanticRequirements + StylePack → ResolvedVisualConfig.

ZERO aesthetic knowledge. Pure semantic translation.
"""

from __future__ import annotations

from ..style_system.style_schema import SemanticRequirements


def map_to_semantic_requirements(slide: dict, index: int, total: int,
                                  narrative_arc: dict = None) -> SemanticRequirements:
    """Map a single slide's state to semantic requirements.

    This is a pure function: state in → semantics out.
    No colors, no fonts, no spacing. Only WHAT the slide is.
    """
    n_role = slide.get("narrative_role", "")
    e_role = slide.get("emotional_role", "")
    s_role = slide.get("structural_role", "")
    rhythm = slide.get("rhythm", {}) or {}
    design = slide.get("design", {}) or {}
    rel_next = slide.get("relation_to_next", "")
    rel_prev = slide.get("relation_to_prev", "")

    intensity = rhythm.get("intensity", 3)
    pace = rhythm.get("pace", "moderate")
    emphasis = design.get("emphasis_level", "normal")

    # Derive contrast and mood from narrative_role
    contrast_map = {
        "hook": "high", "context": "low", "evidence": "medium",
        "insight": "high", "conflict": "maximum", "escalation": "maximum",
        "release": "low", "vision": "medium", "recap": "low",
        "call_to_action": "high", "breathing_page": "low",
    }

    mood_map = {
        "hook": "brand", "context": "neutral", "evidence": "light",
        "insight": "accent", "conflict": "dark", "escalation": "dark",
        "release": "light", "vision": "light", "recap": "neutral",
        "call_to_action": "brand", "breathing_page": "neutral",
    }

    # Determine which act the slide belongs to
    position_pct = (index / max(total - 1, 1)) * 100
    act = _determine_act(position_pct, narrative_arc)

    return SemanticRequirements(
        narrative_role=n_role,
        emotional_role=e_role,
        structural_role=s_role,
        intensity=min(5, max(1, intensity)),
        pace=pace,
        emphasis_level=emphasis,
        contrast_level=contrast_map.get(n_role, "medium"),
        mood=mood_map.get(n_role, "neutral"),
        relation_to_next=rel_next,
        relation_to_prev=rel_prev,
        is_first=(index == 0),
        is_last=(index == total - 1),
        position_pct=position_pct,
        act=act,
    )


def _determine_act(position_pct: float, narrative_arc: dict = None) -> str:
    """Determine which narrative act a position belongs to."""
    if narrative_arc:
        sections = narrative_arc.get("sections", [])
        for sec in sections:
            sr = sec.get("slide_range", [])
            if len(sr) == 2:
                sec_pct_start = (sr[0] / max(sr[1], 1)) * 100 if sr[1] > 0 else 0
                # Approximate: check if position is within this section
                label = sec.get("label", "").lower()
                if "open" in label or "intro" in label or "hook" in label:
                    if position_pct < 20:
                        return "opening"
                elif "climax" in label or "peak" in label:
                    if 40 <= position_pct <= 75:
                        return "climax"
                elif "close" in label or "end" in label or "cta" in label:
                    if position_pct > 80:
                        return "closing"
                elif "release" in label or "resolve" in label or "relief" in label:
                    if 65 <= position_pct <= 90:
                        return "release"

    # Fallback: position-based
    if position_pct < 15:
        return "opening"
    elif position_pct < 35:
        return "build"
    elif position_pct < 70:
        return "climax"
    elif position_pct < 85:
        return "release"
    else:
        return "closing"
