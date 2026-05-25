"""Transition Runtime — slide-to-slide transition definitions.

Purely interprets transition configs from the compiler.
"""

from __future__ import annotations


# Transition runtime is thin — the compiler handles all CSS generation.
# This module exists as an extension point for future transition logic
# that might require JavaScript-driven transitions (e.g., morphing,
# shared-element transitions, FLIP animations).

def get_transition_class(relation_to_next: str, compiler) -> str:
    """Get the CSS class name for a transition type."""
    tl = compiler.pack.transition_language
    spec = tl.relation_transitions.get(relation_to_next, {})
    return f"transition-{spec.get('type', tl.default_transition)}"


def get_transition_duration(relation_to_next: str, compiler) -> int:
    """Get transition duration in ms."""
    tl = compiler.pack.transition_language
    spec = tl.relation_transitions.get(relation_to_next, {})
    return spec.get("duration_ms", tl.default_duration_ms)
