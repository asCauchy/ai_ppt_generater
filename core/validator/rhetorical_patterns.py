"""Rhetorical pattern analysis for slide content.

Pure rule-based detection of rhetorical structures in Chinese presentation text.
No NLP, no embeddings — regex + keyword lexicon matching.
"""

from __future__ import annotations

import re
from .lexicons.rhetorical_vocab import (
    QUESTION_PATTERNS,
    CONTRAST_PATTERNS,
    FUTURE_PATTERNS,
    ACTION_PATTERNS,
    TENSION_PATTERNS,
    RESOLUTION_PATTERNS,
    AGENDA_OPENING_PATTERNS,
    SURPRISE_PATTERNS,
    GENERIC_EXPLANATION_PATTERNS,
    match_any,
    count_matches,
    get_all_text,
)


def has_question(text: str) -> bool:
    """Detect presence of rhetorical or direct questions."""
    return match_any(text, QUESTION_PATTERNS)


def has_contrast(text: str) -> bool:
    """Detect contrast/tension structure (A vs B, past vs present, etc.)."""
    return match_any(text, CONTRAST_PATTERNS)


def has_future_orientation(text: str) -> bool:
    """Detect future-oriented language."""
    return match_any(text, FUTURE_PATTERNS)


def has_action_language(text: str) -> bool:
    """Detect action verbs, imperatives, or invitation language."""
    return match_any(text, ACTION_PATTERNS)


def has_tension(text: str) -> bool:
    """Detect tension/crisis/problem language."""
    return match_any(text, TENSION_PATTERNS)


def has_resolution(text: str) -> bool:
    """Detect resolution/relief language."""
    return match_any(text, RESOLUTION_PATTERNS)


def has_surprise(text: str) -> bool:
    """Detect surprise/unexpected framing."""
    return match_any(text, SURPRISE_PATTERNS)


def is_agenda_opening(text: str) -> bool:
    """Detect weak agenda-style opening."""
    return match_any(text, AGENDA_OPENING_PATTERNS)


def is_generic(text: str) -> bool:
    """Detect generic explanation patterns (boring)."""
    return match_any(text, GENERIC_EXPLANATION_PATTERNS)


def analyze_hook_effectiveness(slide: dict) -> dict:
    """Analyze a hook slide for rhetorical effectiveness.

    Returns dict with:
        has_technique: bool
        techniques_found: list of technique names
        is_weak: bool (true if it's an agenda-style opening)
        excerpt: first 100 chars of content
    """
    text = get_all_text(slide)
    lead = (slide.get("content") or {}).get("lead", "") or ""

    techniques = {
        "question": has_question(text),
        "contrast": has_contrast(text),
        "surprise": has_surprise(text),
        "tension": has_tension(text),
    }

    techniques_found = [k for k, v in techniques.items() if v]
    is_weak = is_agenda_opening(lead) and len(techniques_found) == 0

    return {
        "has_technique": len(techniques_found) > 0,
        "techniques_found": techniques_found,
        "is_weak": is_weak,
        "excerpt": lead[:120] if lead else "",
    }


def analyze_conflict_depth(slide: dict) -> dict:
    """Analyze a conflict slide for genuine tension.

    Returns dict with:
        has_tension: bool
        has_problem: bool
        has_risk: bool
        has_limitation: bool
        has_stakes: bool
        dimension_count: int
        is_balanced_procon: bool
    """
    text = get_all_text(slide)
    content = slide.get("content", {}) or {}
    points = content.get("points", []) or []

    # Check for balanced pro/con structure (weak conflict)
    positive_count = 0
    negative_count = 0
    for pt in points:
        if match_any(pt, [r"突破", r"领先", r"优势", r"成就", r"成功", r"进步", r"增长"]):
            positive_count += 1
        if match_any(pt, [r"挑战", r"不足", r"落后", r"差距", r"问题", r"制约", r"困难"]):
            negative_count += 1

    result = {
        "has_tension": has_tension(text),
        "has_problem": match_any(text, [r"问题|挑战|困难|瓶颈|障碍"]),
        "has_risk": match_any(text, [r"风险|危机|威胁|危险|隐患"]),
        "has_limitation": match_any(text, [r"不足|缺乏|短缺|制约|受限|缺口|只能|仅能"]),
        "has_stakes": match_any(text, [r"如果.*不|一旦|否则|后果|代价|损失|错过"]),
        "dimension_count": 0,
        "is_balanced_procon": False,
    }

    for k in ["has_tension", "has_problem", "has_risk", "has_limitation", "has_stakes"]:
        if result[k]:
            result["dimension_count"] += 1

    # Detect pro/con balance: if positive ≈ negative, it's not genuine conflict
    if positive_count >= 2 and negative_count >= 2 and abs(positive_count - negative_count) <= 1:
        result["is_balanced_procon"] = True

    return result


def analyze_cta_strength(slide: dict) -> dict:
    """Analyze a CTA slide for action-orientation.

    Returns dict with:
        has_action_verb: bool
        has_audience_direction: bool
        has_imperative: bool
        technique_count: int
        is_weak_summary: bool
    """
    text = get_all_text(slide)
    content = slide.get("content", {}) or {}
    lead = content.get("lead", "") or ""

    result = {
        "has_action_verb": has_action_language(text),
        "has_audience_direction": match_any(text, [r"你|你们|大家|每个人|我们.*一起|在座"]),
        "has_imperative": match_any(text, [r"！|吧|请|让.*我们|必须|不要.*等待|现在.*就是"]),
        "technique_count": 0,
        "is_weak_summary": False,
    }

    for k in ["has_action_verb", "has_audience_direction", "has_imperative"]:
        if result[k]:
            result["technique_count"] += 1

    # Check if it's just a summary disguised as CTA
    summary_patterns = [r"以上就是", r"总之", r"总结", r"综上所述", r"回顾"]
    if match_any(lead, summary_patterns) and result["technique_count"] < 2:
        result["is_weak_summary"] = True

    return result


def analyze_vision_orientation(slide: dict) -> dict:
    """Analyze a vision slide for future orientation."""
    text = get_all_text(slide)

    result = {
        "has_future": has_future_orientation(text),
        "has_possibility": match_any(text, [r"可能|可以|能够|潜力|空间|机会"]),
        "has_long_term": match_any(text, [r"长期|长远|战略|趋势|方向|路径|十年"]),
        "dimension_count": 0,
        "is_current_state": False,
    }

    for k in ["has_future", "has_possibility", "has_long_term"]:
        if result[k]:
            result["dimension_count"] += 1

    # Check if it's describing current state instead of future
    current_patterns = [r"已经", r"目前", r"现在", r"当前", r"过去.*年"]
    if match_any(text, current_patterns) and not result["has_future"]:
        result["is_current_state"] = True

    return result


def analyze_emotional_content_consistency(slide: dict) -> dict:
    """Check if content tone is consistent with declared emotional_role."""
    text = get_all_text(slide)
    e_role = slide.get("emotional_role", "")

    if not e_role or not text:
        return {"consistent": True, "mismatches": []}

    from .lexicons.emotional_vocab import EMOTION_KEYWORDS, EMOTION_FORBIDDEN

    mismatches = []

    # Check for expected keywords
    if e_role in EMOTION_KEYWORDS:
        expected = EMOTION_KEYWORDS[e_role]
        strong_found = any(re.search(p, text) for p in expected.get("strong", []))
        weak_found = any(re.search(p, text) for p in expected.get("weak", []))
        if not strong_found and not weak_found:
            mismatches.append(f"no {e_role} keywords found in content")

    # Check for forbidden patterns
    if e_role in EMOTION_FORBIDDEN:
        for forbidden in EMOTION_FORBIDDEN[e_role]:
            if re.search(forbidden, text):
                mismatches.append(f"forbidden pattern '{forbidden}' for {e_role}")

    return {
        "consistent": len(mismatches) == 0,
        "mismatches": mismatches,
    }
