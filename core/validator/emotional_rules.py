"""Emotional alignment validation rules.

Validates emotional consistency across:
  - emotional_role vs. content tone
  - emotional_role vs. rhythm.emotional_state
  - emotional_role vs. narrative_role
"""

from __future__ import annotations

import re
from typing import Optional

from .types import ValidationIssue

from .lexicons.emotional_vocab import EMOTION_KEYWORDS, EMOTION_FORBIDDEN, JARRING_TRANSITIONS
from .lexicons.rhetorical_vocab import get_all_text
from .rhetorical_patterns import analyze_emotional_content_consistency


LAYER = "semantic"

RULE_E01 = "E01"  # emotional_role vs content tone
RULE_E02 = "E02"  # emotional_role vs rhythm.emotional_state
RULE_E03 = "E03"  # emotional_role vs narrative_role
RULE_E04 = "E04"  # emotional transition check


def _issue(rule: str, severity: str, message: str, location: str,
           context: dict = None, suggested_fix: str = None) -> ValidationIssue:
    return ValidationIssue(LAYER, rule, severity, message, location, context, suggested_fix)


# ---------------------------------------------------------------------------
# E01: emotional_role vs content tone
# ---------------------------------------------------------------------------

def check_emotional_content_alignment(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if emotional_role is consistent with actual content tone."""
    issues = []
    loc = f"$.slides[{index}]"
    e_role = slide.get("emotional_role", "")
    text = get_all_text(slide)

    if not e_role or not text:
        return issues

    analysis = analyze_emotional_content_consistency(slide)

    if not analysis["consistent"]:
        for mismatch in analysis["mismatches"]:
            issues.append(_issue(RULE_E01, "warning",
                f"emotional_role='{e_role}' conflicts with content tone: {mismatch}",
                loc, {
                    "emotional_role": e_role,
                    "mismatch": mismatch,
                    "content_excerpt": text[:150],
                },
                suggested_fix=f"Either change emotional_role to match actual content tone, or rewrite content to include {e_role}-congruent language."))

    return issues


# ---------------------------------------------------------------------------
# E02: emotional_role vs rhythm.emotional_state
# ---------------------------------------------------------------------------

# Semantic equivalence classes for emotional states
EMOTIONAL_EQUIVALENCE = {
    "curious": {"curious", "engaged", "focused"},
    "shocked": {"shocked", "surprised"},
    "concerned": {"concerned", "skeptical", "worried"},
    "inspired": {"inspired", "excited", "hopeful"},
    "determined": {"determined", "confident", "motivated"},
    "reflective": {"reflective", "calm", "thoughtful"},
    "confident": {"confident", "determined", "convinced"},
    "impressed": {"impressed", "convinced"},
    "surprised": {"surprised", "shocked", "curious"},
    "excited": {"excited", "inspired", "enthusiastic"},
    "engaged": {"engaged", "focused", "curious"},
    "convinced": {"convinced", "impressed", "confident"},
    "focused": {"focused", "engaged"},
    "hopeful": {"hopeful", "inspired", "optimistic"},
    "skeptical": {"skeptical", "concerned"},
    "motivated": {"motivated", "determined", "inspired"},
}

# Direct contradictions
EMOTIONAL_CONTRADICTIONS = {
    ("shocked", "reflective"),
    ("excited", "solemn"),
    ("concerned", "relieved"),
    ("skeptical", "convinced"),
    ("skeptical", "confident"),
    ("hopeful", "concerned"),
    ("determined", "skeptical"),
    ("inspired", "skeptical"),
    ("surprised", "reflective"),
    ("curious", "determined"),
}


def check_emotional_state_alignment(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if emotional_role is aligned with rhythm.emotional_state."""
    issues = []
    loc = f"$.slides[{index}]"
    e_role = slide.get("emotional_role", "")
    rhythm = slide.get("rhythm", {}) or {}
    r_state = rhythm.get("emotional_state", "")

    if not e_role or not r_state:
        return issues

    # Normalize and check equivalence
    e_key = e_role.lower().strip()
    r_key = r_state.lower().strip()

    if e_key == r_key:
        return issues  # exact match

    # Check equivalence class
    if e_key in EMOTIONAL_EQUIVALENCE and r_key in EMOTIONAL_EQUIVALENCE[e_key]:
        return issues  # in same equivalence class

    # Check contradiction
    pair = tuple(sorted([e_key, r_key]))
    if pair in {(tuple(sorted(p)) for p in EMOTIONAL_CONTRADICTIONS)}:
        pass  # we need to check properly

    # Manual contradiction check (more reliable than set conversion)
    for c1, c2 in EMOTIONAL_CONTRADICTIONS:
        if (e_key == c1 and r_key == c2) or (e_key == c2 and r_key == c1):
            issues.append(_issue(RULE_E02, "warning",
                f"emotional_role='{e_role}' contradicts rhythm.emotional_state='{r_state}'",
                loc, {
                    "emotional_role": e_role,
                    "rhythm_emotional_state": r_state,
                    "relationship": "contradiction",
                },
                suggested_fix=f"Align emotional_role with rhythm.emotional_state='{r_state}' which was set by NarrativePlanner. Choose an emotional_role in the same equivalence class."))
            return issues

    # Different but not contradictory — suggestion
    issues.append(_issue(RULE_E02, "suggestion",
        f"emotional_role='{e_role}' differs from rhythm.emotional_state='{r_state}'",
        loc, {
            "emotional_role": e_role,
            "rhythm_emotional_state": r_state,
            "relationship": "mismatch",
        }))

    return issues


# ---------------------------------------------------------------------------
# E03: emotional_role vs narrative_role compatibility
# ---------------------------------------------------------------------------

# Extended compatibility matrix
NARRATIVE_EMOTIONAL_SUSPECT_EXTENDED = {
    # Original pairs from validator
    ("hook", "solemn"),
    ("hook", "relieved"),
    ("breathing_page", "shocked"),
    ("breathing_page", "excited"),
    ("call_to_action", "reflective"),
    ("call_to_action", "skeptical"),
    ("conflict", "relieved"),
    ("conflict", "excited"),
    ("vision", "skeptical"),
    ("vision", "concerned"),
    ("evidence", "shocked"),
    # Extended pairs
    ("hook", "reflective"),
    ("hook", "skeptical"),
    ("conflict", "hopeful"),
    ("conflict", "inspired"),
    ("release", "concerned"),
    ("release", "shocked"),
    ("escalation", "relieved"),
    ("escalation", "confident"),
    ("vision", "reflective"),
    ("recap", "shocked"),
    ("recap", "excited"),
    ("call_to_action", "concerned"),
    ("call_to_action", "skeptical"),
    ("context", "shocked"),
    ("context", "excited"),
    ("evidence", "skeptical"),
    ("insight", "determined"),
}


def check_narrative_emotional_compatibility(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if emotional_role is compatible with narrative_role."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")
    e_role = slide.get("emotional_role", "")

    if not n_role or not e_role:
        return issues

    pair = (n_role, e_role)
    if pair in NARRATIVE_EMOTIONAL_SUSPECT_EXTENDED:
        issues.append(_issue(RULE_E03, "suggestion",
            f"narrative_role='{n_role}' + emotional_role='{e_role}' is a suspect combination",
            loc, {
                "narrative_role": n_role,
                "emotional_role": e_role,
                "suggested_fix": f"Consider a different emotional tone for '{n_role}' slides",
            }))

    return issues


# ---------------------------------------------------------------------------
# E04: Emotional transition smoothness
# ---------------------------------------------------------------------------

def check_emotional_transition(slide: dict, index: int, prev_slide: Optional[dict] = None) -> list[ValidationIssue]:
    """Check for jarring emotional transitions between adjacent slides."""
    issues = []

    if not prev_slide:
        return issues

    loc = f"$.slides[{index-1}]→slides[{index}]"
    prev_e = prev_slide.get("emotional_role", "")
    curr_e = slide.get("emotional_role", "")
    prev_r = (prev_slide.get("rhythm") or {}).get("emotional_state", "")
    curr_r = (slide.get("rhythm") or {}).get("emotional_state", "")

    if not prev_e or not curr_e:
        return issues

    # Check both emotional_role and rhythm emotional_state transitions
    transition1 = (prev_e, curr_e)
    transition2 = (prev_r, curr_r)

    if transition1 in JARRING_TRANSITIONS:
        issues.append(_issue(RULE_E04, "suggestion",
            f"Jarring emotional_role transition: {prev_e} → {curr_e}",
            loc, {
                "from_emotional_role": prev_e,
                "to_emotional_role": curr_e,
            }))

    if transition2 in JARRING_TRANSITIONS:
        issues.append(_issue(RULE_E04, "suggestion",
            f"Jarring rhythm emotional_state transition: {prev_r} → {curr_r}",
            loc, {
                "from_rhythm_state": prev_r,
                "to_rhythm_state": curr_r,
            }))

    return issues


# ---------------------------------------------------------------------------
# Rule Aggregator
# ---------------------------------------------------------------------------

def run_all_emotional_checks(state: dict) -> list[ValidationIssue]:
    """Run all emotional alignment checks on the presentation state."""
    issues = []
    slides = state.get("slides", [])

    for i, slide in enumerate(slides):
        prev_slide = slides[i - 1] if i > 0 else None

        issues.extend(check_emotional_content_alignment(slide, i))
        issues.extend(check_emotional_state_alignment(slide, i))
        issues.extend(check_narrative_emotional_compatibility(slide, i))
        issues.extend(check_emotional_transition(slide, i, prev_slide))

    return issues
