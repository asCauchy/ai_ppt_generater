"""Motion Runtime — CSS and JS for motion primitives.

This is a PURE interpretation runtime. It consumes the StyleCompiler's
motion output and provides the renderer with animation CSS/JS.
Zero aesthetic knowledge.
"""

from __future__ import annotations


def compile_motion(compiler) -> dict:
    """Compile all motion CSS and JS from the compiler.

    Returns a dict with 'css' and 'js_config' keys for the renderer.
    """
    return {
        "css": compiler.compile_motion_css(),
    }


def compile_transitions(compiler) -> dict:
    """Compile all transition CSS from the compiler."""
    return {
        "css": compiler.compile_transition_css(),
    }
