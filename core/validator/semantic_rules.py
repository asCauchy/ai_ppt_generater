"""Semantic content validation rules.

Validates narrative integrity by checking whether declared narrative_role
is genuinely realized in slide content. Rule-based, no NLP.
"""

from __future__ import annotations

import re
from typing import Optional

from .types import ValidationIssue

from .lexicons.narrative_vocab import NARRATIVE_ROLE_REQUIRED, STRUCTURAL_ROLE_CONSTRAINTS
from .lexicons.rhetorical_vocab import get_all_text
from .rhetorical_patterns import (
    analyze_hook_effectiveness,
    analyze_conflict_depth,
    analyze_cta_strength,
    analyze_vision_orientation,
)


# ---------------------------------------------------------------------------
# Rule identifiers
# ---------------------------------------------------------------------------

LAYER = "semantic"

# Narrative Role Presence rules
RULE_N01 = "N01"  # hook presence
RULE_N02 = "N02"  # conflict presence
RULE_N03 = "N03"  # escalation presence
RULE_N04 = "N04"  # release presence
RULE_N05 = "N05"  # vision presence
RULE_N06 = "N06"  # CTA presence


def _issue(rule: str, severity: str, message: str, location: str,
           context: dict = None, suggested_fix: str = None) -> ValidationIssue:
    return ValidationIssue(LAYER, rule, severity, message, location, context, suggested_fix)


# ---------------------------------------------------------------------------
# Rule: Hook Effectiveness (N01)
# ---------------------------------------------------------------------------

def check_hook(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if hook slide has genuine opening technique."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "hook":
        return issues

    analysis = analyze_hook_effectiveness(slide)

    if analysis["is_weak"]:
        issues.append(_issue(RULE_N01, "warning",
            "Hook slide uses agenda-style opening — lacks engagement technique",
            loc, {
                "narrative_role": "hook",
                "techniques_found": [],
                "content_excerpt": analysis["excerpt"],
            },
            suggested_fix="Rewrite opening with a question, surprising data point, or strong contrast. Avoid '本次汇报主要介绍' patterns."))
    elif not analysis["has_technique"]:
        issues.append(_issue(RULE_N01, "suggestion",
            "Hook slide lacks rhetorical technique (question/contrast/surprise/tension)",
            loc, {
                "narrative_role": "hook",
                "techniques_found": [],
                "required_minimum": "at least one of: question, contrast, surprise, tension",
                "content_excerpt": analysis["excerpt"],
            },
            suggested_fix="Add a rhetorical question, a surprising statistic, or a 'not X but Y' contrast to engage the audience."))
    else:
        # Hook has technique — still check richness
        if len(analysis["techniques_found"]) == 1:
            issues.append(_issue(RULE_N01, "suggestion",
                f"Hook slide only uses one technique: {analysis['techniques_found'][0]}. Consider adding contrast or tension.",
                loc, {
                    "narrative_role": "hook",
                    "techniques_found": analysis["techniques_found"],
                }))

    return issues


# ---------------------------------------------------------------------------
# Rule: Conflict Depth (N02)
# ---------------------------------------------------------------------------

def check_conflict(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if conflict slide has genuine tension/stakes language."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "conflict":
        return issues

    analysis = analyze_conflict_depth(slide)
    text = get_all_text(slide)

    if analysis["is_balanced_procon"]:
        issues.append(_issue(RULE_N02, "warning",
            "Conflict slide is a balanced pro/con list — lacks genuine tension",
            loc, {
                "narrative_role": "conflict",
                "issue": "balanced_procon_structure",
                "content_excerpt": text[:150],
            },
            suggested_fix="Restructure to make tension dominant. Lead with stakes ('If X fails...'). Keep positive evidence in evidence slides, not conflict slides."))

    if analysis["dimension_count"] < 2:
        issues.append(_issue(RULE_N02, "warning",
            f"Conflict slide has only {analysis['dimension_count']} tension dimension(s) — needs ≥2",
            loc, {
                "narrative_role": "conflict",
                "detected_dimensions": {
                    "tension": analysis["has_tension"],
                    "problem": analysis["has_problem"],
                    "risk": analysis["has_risk"],
                    "limitation": analysis["has_limitation"],
                    "stakes": analysis["has_stakes"],
                },
                "content_excerpt": text[:150],
            },
            suggested_fix="Add risk language (危机/威胁), limitation language (不足/缺口), and stakes language (如果...不/后果) to establish genuine tension."))

    # Check for forbidden neutralization patterns
    forbidden = NARRATIVE_ROLE_REQUIRED.get("conflict", {}).get("forbidden_patterns", [])
    for pat in forbidden:
        if re.search(pat, text):
            issues.append(_issue(RULE_N02, "warning",
                f"Conflict slide contains neutralizing pattern: '{pat}'",
                loc, {
                    "narrative_role": "conflict",
                    "matched_pattern": pat,
                }))
            break  # one is enough

    return issues


# ---------------------------------------------------------------------------
# Rule: Escalation Continuity (N03)
# ---------------------------------------------------------------------------

def check_escalation(slide: dict, index: int, prev_slide: Optional[dict] = None) -> list[ValidationIssue]:
    """Check if escalation slide actually escalates from previous."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "escalation":
        return issues

    text = get_all_text(slide)
    current_intensity = (slide.get("rhythm") or {}).get("intensity", 3)

    # Check for intensifying language
    required = NARRATIVE_ROLE_REQUIRED.get("escalation", {})
    required_patterns = required.get("patterns", {})
    pattern_count = 0
    for group, patterns in required_patterns.items():
        if any(re.search(p, text) for p in patterns):
            pattern_count += 1

    if pattern_count == 0:
        issues.append(_issue(RULE_N03, "warning",
            "Escalation slide lacks intensifying/raising-stakes/deepening language",
            loc, {
                "narrative_role": "escalation",
                "detected_patterns": pattern_count,
                "content_excerpt": text[:150],
            }))

    # Check intensity increase relative to previous slide
    if prev_slide:
        prev_intensity = (prev_slide.get("rhythm") or {}).get("intensity", 3)
        if current_intensity < prev_intensity:
            issues.append(_issue(RULE_N03, "warning",
                f"Escalation slide intensity ({current_intensity}) is lower than previous ({prev_intensity})",
                loc, {
                    "current_intensity": current_intensity,
                    "previous_intensity": prev_intensity,
                }))
        elif current_intensity == prev_intensity:
            issues.append(_issue(RULE_N03, "suggestion",
                f"Escalation slide intensity ({current_intensity}) equals previous — no perceived escalation",
                loc, {
                    "current_intensity": current_intensity,
                    "previous_intensity": prev_intensity,
                }))

    return issues


# ---------------------------------------------------------------------------
# Rule: Release Validity (N04)
# ---------------------------------------------------------------------------

def check_release(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if release slide provides genuine relief/resolution."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "release":
        return issues

    text = get_all_text(slide)

    required = NARRATIVE_ROLE_REQUIRED.get("release", {})
    required_patterns = required.get("patterns", {})
    pattern_count = 0
    for group, patterns in required_patterns.items():
        if any(re.search(p, text) for p in patterns):
            pattern_count += 1

    if pattern_count == 0:
        issues.append(_issue(RULE_N04, "warning",
            "Release slide lacks relief/clarity/hope/stability language",
            loc, {
                "narrative_role": "release",
                "required_patterns": list(required_patterns.keys()),
                "content_excerpt": text[:150],
            }))

    # Check for forbidden crisis patterns in release
    forbidden = required.get("forbidden_patterns", [])
    for pat in forbidden:
        if re.search(pat, text):
            issues.append(_issue(RULE_N04, "warning",
                f"Release slide contains unresolved crisis language: '{pat}'",
                loc, {
                    "narrative_role": "release",
                    "matched_pattern": pat,
                }))
            break

    return issues


# ---------------------------------------------------------------------------
# Rule: Vision Orientation (N05)
# ---------------------------------------------------------------------------

def check_vision(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if vision slide is genuinely future-oriented."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "vision":
        return issues

    analysis = analyze_vision_orientation(slide)
    text = get_all_text(slide)

    if analysis["is_current_state"]:
        issues.append(_issue(RULE_N05, "warning",
            "Vision slide describes current state, not future vision",
            loc, {
                "narrative_role": "vision",
                "issue": "present_tense_dominance",
                "content_excerpt": text[:150],
            },
            suggested_fix="Reframe with future-oriented language: 'By 2030...', 'The next decade will...', 'Imagine a world where...'. Move current-state data to evidence slides."))

    if analysis["dimension_count"] < 2:
        issues.append(_issue(RULE_N05, "warning",
            f"Vision slide has only {analysis['dimension_count']} future dimension(s) — needs ≥2",
            loc, {
                "narrative_role": "vision",
                "detected_dimensions": {
                    "future": analysis["has_future"],
                    "possibility": analysis["has_possibility"],
                    "long_term": analysis["has_long_term"],
                },
                "content_excerpt": text[:150],
            },
            suggested_fix="Add future milestones (未来/十年/即将), possibility framing (可能/潜力/空间), and long-term perspective (战略/趋势/方向)."))

    # Check for forbidden retrospective patterns
    forbidden = NARRATIVE_ROLE_REQUIRED.get("vision", {}).get("forbidden_patterns", [])
    for pat in forbidden:
        if re.search(pat, text):
            issues.append(_issue(RULE_N03, "suggestion",  # reuse N03 slot as suggestion
                f"Vision slide contains retrospective language: '{pat}'",
                loc, {"narrative_role": "vision", "matched_pattern": pat}))
            break

    return issues


# ---------------------------------------------------------------------------
# Rule: CTA Strength (N06)
# ---------------------------------------------------------------------------

def check_cta(slide: dict, index: int) -> list[ValidationIssue]:
    """Check if CTA slide has genuine call-to-action language."""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role != "call_to_action":
        return issues

    analysis = analyze_cta_strength(slide)
    text = get_all_text(slide)

    if analysis["is_weak_summary"]:
        issues.append(_issue(RULE_N06, "warning",
            "CTA slide is a summary disguised as call-to-action — lacks imperative/invitation",
            loc, {
                "narrative_role": "call_to_action",
                "issue": "weak_summary_cta",
                "content_excerpt": text[:150],
            },
            suggested_fix="Replace summary language with direct action: use action verbs (加入/参与/开始), address the audience (你/你们), and create urgency (现在就是/不要等待)."))

    if analysis["technique_count"] < 2:
        issues.append(_issue(RULE_N06, "warning",
            f"CTA slide has only {analysis['technique_count']} action technique(s) — needs ≥2",
            loc, {
                "narrative_role": "call_to_action",
                "detected_techniques": {
                    "action_verb": analysis["has_action_verb"],
                    "audience_direction": analysis["has_audience_direction"],
                    "imperative": analysis["has_imperative"],
                },
                "required_techniques": ["action_verb", "audience_direction/imperative"],
                "content_excerpt": text[:150],
            },
            suggested_fix="Add at least: one action verb (加入/参与/开始/行动) and one audience-directed imperative (你/你们/让/请/现在). End with an exclamation or invitation."))

    return issues


# ---------------------------------------------------------------------------
# Rule: Generic Narrative Role Check (fallback for other roles)
# ---------------------------------------------------------------------------

def check_narrative_role_content(slide: dict, index: int) -> list[ValidationIssue]:
    """Generic check: does the content at least partially match the declared narrative_role?"""
    issues = []
    loc = f"$.slides[{index}]"
    n_role = slide.get("narrative_role", "")

    if n_role not in NARRATIVE_ROLE_REQUIRED:
        return issues

    text = get_all_text(slide)
    spec = NARRATIVE_ROLE_REQUIRED[n_role]
    required_patterns = spec.get("patterns", {})
    min_matches = spec.get("min_matches", 1)
    forbidden = spec.get("forbidden_patterns", [])

    # Count matching pattern groups
    match_count = 0
    matched_groups = []
    for group, patterns in required_patterns.items():
        if any(re.search(p, text) for p in patterns):
            match_count += 1
            matched_groups.append(group)

    if match_count < min_matches:
        required_groups = list(required_patterns.keys())
        issues.append(_issue("N07", "suggestion",
            f"narrative_role='{n_role}' content matches only {match_count}/{min_matches} required pattern groups",
            loc, {
                "narrative_role": n_role,
                "matched_groups": matched_groups,
                "required_groups": required_groups,
                "content_excerpt": text[:150],
            }))

    # Check forbidden patterns
    for pat in forbidden:
        if re.search(pat, text):
            issues.append(_issue("N08", "warning",
                f"narrative_role='{n_role}' contains forbidden pattern: '{pat}'",
                loc, {
                    "narrative_role": n_role,
                    "matched_pattern": pat,
                }))
            break

    return issues


# ---------------------------------------------------------------------------
# Rule: Structural Role Constraints
# ---------------------------------------------------------------------------

def check_structural_role_constraints(slide: dict, index: int, total_slides: int) -> list[ValidationIssue]:
    """Check structural_role position legality."""
    issues = []
    loc = f"$.slides[{index}]"
    s_role = slide.get("structural_role", "")
    n_role = slide.get("narrative_role", "")

    if s_role not in STRUCTURAL_ROLE_CONSTRAINTS:
        return issues

    constraints = STRUCTURAL_ROLE_CONSTRAINTS[s_role]

    # Check position
    expected_positions = constraints.get("expected_positions", [])
    if expected_positions:
        is_expected = False
        for ep in expected_positions:
            if ep == -1:
                if index == total_slides - 1:
                    is_expected = True
            elif ep == -2:
                if index in (total_slides - 1, total_slides - 2):
                    is_expected = True
            elif index == ep:
                is_expected = True
        if not is_expected:
            issues.append(_issue("N09", "suggestion",
                f"structural_role='{s_role}' at position {index}, expected positions: {expected_positions}",
                loc, {"structural_role": s_role, "position": index}))

    # Check forbidden narrative roles
    forbidden_roles = constraints.get("forbidden_narrative_roles", [])
    if n_role in forbidden_roles:
        issues.append(_issue("N10", "warning",
            f"structural_role='{s_role}' should not have narrative_role='{n_role}'",
            loc, {"structural_role": s_role, "narrative_role": n_role}))

    return issues


# ---------------------------------------------------------------------------
# Rule Aggregator: run all semantic content checks on all slides
# ---------------------------------------------------------------------------

def run_all_semantic_content_checks(state: dict) -> list[ValidationIssue]:
    """Run all narrative role presence checks on the presentation state.

    Returns a list of ValidationIssue objects.
    """
    issues = []
    slides = state.get("slides", [])
    n = len(slides)

    for i, slide in enumerate(slides):
        n_role = slide.get("narrative_role", "")
        prev_slide = slides[i - 1] if i > 0 else None

        # N01-N06: Role-specific checks
        if n_role == "hook":
            issues.extend(check_hook(slide, i))
        elif n_role == "conflict":
            issues.extend(check_conflict(slide, i))
        elif n_role == "escalation":
            issues.extend(check_escalation(slide, i, prev_slide))
        elif n_role == "release":
            issues.extend(check_release(slide, i))
        elif n_role == "vision":
            issues.extend(check_vision(slide, i))
        elif n_role == "call_to_action":
            issues.extend(check_cta(slide, i))

        # N07-N08: Generic content-role match
        if n_role in NARRATIVE_ROLE_REQUIRED:
            issues.extend(check_narrative_role_content(slide, i))

        # N09-N10: Structural role constraints
        issues.extend(check_structural_role_constraints(slide, i, n))

    return issues
