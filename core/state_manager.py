"""Presentation State Manager — deep merge, diff, identity resolution.

Key invariant: slides are merged by index identity, not by array position.
This allows agents to return partial slide updates without disturbing sibling slides.
"""

from __future__ import annotations
import copy
from datetime import datetime, timezone


def deep_merge(base: dict, overlay: dict) -> dict:
    """Recursive merge, overlay wins. Lists of dicts with 'index' key are merged by index."""
    result = copy.deepcopy(base)

    for key, value in overlay.items():
        if key not in result:
            result[key] = copy.deepcopy(value)
        elif _is_dict(result[key]) and _is_dict(value):
            result[key] = deep_merge(result[key], value)
        elif _is_list(result[key]) and _is_list(value) and _is_indexed_dict_list(value):
            result[key] = _merge_indexed_lists(result[key], value)
        else:
            result[key] = copy.deepcopy(value)

    return result


def create_state_diff(modified: dict, base: dict) -> dict:
    """Return only the keys that differ from base. Used for agent output."""
    diff = {}
    for key, value in modified.items():
        if key not in base:
            diff[key] = copy.deepcopy(value)
        elif _is_dict(value) and _is_dict(base.get(key)):
            sub = create_state_diff(value, base[key])
            if sub:
                diff[key] = sub
        elif value != base.get(key):
            diff[key] = copy.deepcopy(value)
    return diff


def init_presentation_state(topic: str, style: str, pages: int, context_overrides: dict = None) -> dict:
    """Create a minimal, valid Presentation State shell.

    This is the starting state that the pipeline hands to the first agent.
    It contains meta + context filled from user input; all other sections are empty
    or placeholder.
    """
    now = _utcnow()
    ctx = {
        "audience": {"profile": "", "knowledge_level": "mixed"},
        "occasion": {"type": "classroom_lecture", "formality": "semi_formal"},
        "intent": {"primary_goal": "inform"},
        "duration": {"total_minutes": pages * 2},
    }
    if context_overrides:
        ctx = deep_merge(ctx, context_overrides)

    return {
        "meta": {
            "title": topic,
            "style": style,
            "uuid": _shortuuid(),
            "version": "0.1.0",
            "language": "zh-CN",
        },
        "context": ctx,
        "narrative_arc": {"structure": "", "sections": []},
        "rhythm_map": [],
        "slides": [],
        "design_system": _default_design_system(),
        "runtime": {
            "generation_stage": "init",
            "pipeline_version": "1.0",
            "agents_involved": [],
            "history": [],
        },
    }


# ---------------------------------------------------------------------------
# internal helpers
# ---------------------------------------------------------------------------

def _is_dict(v):
    return isinstance(v, dict)


def _is_list(v):
    return isinstance(v, list)


def _is_indexed_dict_list(v):
    return v and isinstance(v[0], dict) and ("index" in v[0] or "id" in v[0])


def _merge_indexed_lists(base_list: list, overlay_list: list) -> list:
    """Merge two lists of dicts, matching by 'index' (primary) or 'id' (fallback)."""
    result = list(base_list)
    index_map = {}
    for i, item in enumerate(result):
        key = item.get("index", item.get("id"))
        if key is not None:
            index_map[key] = i

    for item in overlay_list:
        key = item.get("index", item.get("id"))
        if key is not None and key in index_map:
            result[index_map[key]] = deep_merge(result[index_map[key]], item)
        else:
            result.append(copy.deepcopy(item))
            if key is not None:
                index_map[key] = len(result) - 1

    # Re-sort by index if available
    if all(isinstance(s.get("index"), int) for s in result):
        result.sort(key=lambda s: s.get("index", 0))

    return result


def _default_design_system():
    return {
        "palette": {
            "name": "academic_blue",
            "colors": {
                "primary": "#003D6B",
                "secondary": "#5B9BD5",
                "accent": "#E8A838",
                "neutral": "#F0F2F5",
                "background": "#FFFFFF",
                "text": "#333333",
                "text_light": "#888888",
            },
        },
        "typography": {
            "title_font": "思源黑体",
            "body_font": "微软雅黑",
            "scale": [12, 14, 16, 18, 24, 32, 44, 56],
            "base_size": 16,
        },
        "spacing_unit": 8,
        "corner_style": "rounded",
        "grid_columns": 12,
    }


def _utcnow():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _shortuuid():
    import uuid
    return uuid.uuid4().hex[:12]
