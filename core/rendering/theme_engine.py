"""Theme Engine — Phase P4.

Cinematic surface system. Not CSS gradients — composed lighting,
depth, and atmosphere. Premium visual surfaces inspired by
Linear, Apple, Stripe, Arc.

Principles:
  - Light over decoration
  - Depth over flatness
  - Atmosphere over pattern
  - Subtlety over impact
  - Surface quality over visual noise
"""

from __future__ import annotations
from typing import Optional


# ---------------------------------------------------------------------------
# Theme palette — derived from design system + cinematic enhancement
# ---------------------------------------------------------------------------

def derive_cinematic_palette(ds_colors: dict) -> dict:
    """Enhance design system palette with cinematic surface colors."""
    primary = ds_colors.get("primary", "#003D6B")
    secondary = ds_colors.get("secondary", "#5B9BD5")
    accent = ds_colors.get("accent", "#E8A838")
    bg = ds_colors.get("background", "#FFFFFF")
    text = ds_colors.get("text", "#333333")
    text_light = ds_colors.get("text_light", "#888888")

    return {
        # Core
        "--c-primary": primary,
        "--c-secondary": secondary,
        "--c-accent": accent,
        "--c-bg": bg,
        "--c-text": text,
        "--c-text-light": text_light,

        # Cinematic surfaces — derived from primary/accent
        "--c-surface-dark": _darken(primary, 0.85),
        "--c-surface-mid": _darken(primary, 0.6),
        "--c-surface-light": _lighten(primary, 0.92),
        "--c-surface-glow": _lighten(accent, 0.85),
        "--c-surface-glass": "rgba(255,255,255,0.08)",
        "--c-surface-noise": "rgba(255,255,255,0.03)",

        # Gradients
        "--c-gradient-brand": f"linear-gradient(135deg, {primary} 0%, {secondary} 100%)",
        "--c-gradient-dark": f"linear-gradient(170deg, {_darken(primary, 0.9)} 0%, {_darken(primary, 0.7)} 40%, {_darken(primary, 0.95)} 100%)",
        "--c-gradient-glow": f"radial-gradient(ellipse at 50% 30%, {_lighten(accent, 0.7)} 0%, transparent 70%)",
        "--c-gradient-horizon": f"linear-gradient(180deg, {bg} 0%, {_lighten(accent, 0.9)} 40%, {_lighten(primary, 0.92)} 80%, {bg} 100%)",
        "--c-gradient-accent-wash": f"linear-gradient(135deg, {bg} 0%, {_lighten(accent, 0.88)} 100%)",
        "--c-gradient-tension": f"linear-gradient(160deg, {_darken(primary, 0.95)} 0%, {_darken(primary, 0.8)} 50%, {_darken(secondary, 0.7)} 100%)",
        "--c-gradient-soft": f"linear-gradient(180deg, {bg} 0%, {_lighten(primary, 0.95)} 100%)",
    }


def _darken(hex_color: str, amount: float) -> str:
    """Simple darken by mixing with black."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r * amount)
    g = int(g * amount)
    b = int(b * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


def _lighten(hex_color: str, amount: float) -> str:
    """Simple lighten by mixing with white."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * amount)
    g = int(g + (255 - g) * amount)
    b = int(b + (255 - b) * amount)
    return f"#{r:02x}{g:02x}{b:02x}"


# ---------------------------------------------------------------------------
# Scene → Surface treatment
# ---------------------------------------------------------------------------

SURFACE_TREATMENTS = {
    "hook": {
        "background": "var(--c-gradient-brand)",
        "surface": "none",
        "ambient": "var(--c-gradient-glow)",
        "overlay": "none",
        "text_color": "#ffffff",
        "text_secondary_color": "rgba(255,255,255,0.75)",
        "accent_glow": True,
    },
    "context": {
        "background": "var(--c-bg)",
        "surface": "none",
        "ambient": "none",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": False,
    },
    "evidence": {
        "background": "var(--c-bg)",
        "surface": "var(--c-surface-light)",
        "ambient": "none",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": False,
    },
    "insight": {
        "background": "var(--c-gradient-accent-wash)",
        "surface": "none",
        "ambient": "var(--c-surface-glow)",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": True,
    },
    "conflict": {
        "background": "var(--c-gradient-tension)",
        "surface": "none",
        "ambient": "none",
        "overlay": "none",
        "text_color": "#e0e8f0",
        "text_secondary_color": "rgba(200,210,225,0.7)",
        "accent_glow": False,
    },
    "escalation": {
        "background": "var(--c-gradient-dark)",
        "surface": "none",
        "ambient": "none",
        "overlay": "none",
        "text_color": "#d0d8e8",
        "text_secondary_color": "rgba(180,195,215,0.7)",
        "accent_glow": False,
    },
    "release": {
        "background": "var(--c-gradient-soft)",
        "surface": "none",
        "ambient": "var(--c-gradient-glow)",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": True,
    },
    "vision": {
        "background": "var(--c-gradient-horizon)",
        "surface": "none",
        "ambient": "var(--c-gradient-glow)",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": True,
    },
    "recap": {
        "background": "var(--c-bg)",
        "surface": "var(--c-surface-light)",
        "ambient": "none",
        "overlay": "none",
        "text_color": "var(--c-text)",
        "text_secondary_color": "var(--c-text-light)",
        "accent_glow": False,
    },
    "call_to_action": {
        "background": "var(--c-primary)",
        "surface": "none",
        "ambient": "none",
        "overlay": "none",
        "text_color": "#ffffff",
        "text_secondary_color": "rgba(255,255,255,0.8)",
        "accent_glow": True,
    },
    "breathing_page": {
        "background": "var(--c-bg)",
        "surface": "none",
        "ambient": "none",
        "overlay": "none",
        "text_color": "var(--c-text-light)",
        "text_secondary_color": "rgba(150,150,150,0.5)",
        "accent_glow": False,
    },
}


# ---------------------------------------------------------------------------
# Ambient effects CSS generation
# ---------------------------------------------------------------------------

AMBIENT_CSS = """
/* === Cinematic Surfaces === */

/* Glass surface */
.surface-glass {
  background: rgba(255,255,255,0.06);
  backdrop-filter: blur(40px);
  -webkit-backdrop-filter: blur(40px);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 16px;
}

/* Noise texture overlay */
.noise-overlay::after {
  content: '';
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events: none;
}

/* Ambient glow sphere */
.glow-sphere {
  position: absolute;
  width: 50vw;
  height: 50vw;
  max-width: 600px;
  max-height: 600px;
  border-radius: 50%;
  filter: blur(120px);
  pointer-events: none;
  z-index: 0;
}
.glow-sphere.top-right {
  top: -20%;
  right: -15%;
  background: var(--c-surface-glow);
  opacity: 0.4;
}
.glow-sphere.center {
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  background: var(--c-surface-glow);
  opacity: 0.25;
}
.glow-sphere.bottom {
  bottom: -25%;
  left: 30%;
  background: var(--c-surface-glow);
  opacity: 0.35;
}

/* Accent line */
.accent-line {
  position: absolute;
  background: linear-gradient(90deg, var(--c-accent), transparent);
  height: 1px;
  width: 30%;
  opacity: 0.3;
}
.accent-line.top { top: 8vh; left: 6vw; }
.accent-line.bottom { bottom: 8vh; right: 6vw; transform: scaleX(-1); }

/* Tension lines for conflict/escalation */
.tension-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    linear-gradient(0deg, transparent 0%, rgba(255,255,255,0.02) 50%, transparent 100%),
    repeating-linear-gradient(90deg, transparent, transparent 40px, rgba(255,255,255,0.015) 40px, rgba(255,255,255,0.015) 41px);
}

/* Impact ring for CTA */
.impact-ring {
  position: absolute;
  top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: min(50vw, 500px);
  height: min(50vw, 500px);
  border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.08);
  pointer-events: none;
  z-index: 0;
}

/* Rising gradient for escalation */
.rising-gradient {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  height: 40%;
  background: linear-gradient(0deg, rgba(255,255,255,0.04) 0%, transparent 100%);
  pointer-events: none;
  z-index: 0;
}

/* Depth shadow on surface panels */
.surface-panel {
  background: var(--c-surface-light);
  border-radius: 12px;
  padding: 2em;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 16px rgba(0,0,0,0.03);
}

/* Ambient dust particles (subtle) */
.accent-dust {
  position: absolute;
  pointer-events: none;
  z-index: 0;
  width: 100%;
  height: 100%;
  top: 0; left: 0;
  background:
    radial-gradient(1px 1px at 20% 30%, var(--c-accent), transparent),
    radial-gradient(1px 1px at 60% 70%, var(--c-accent), transparent),
    radial-gradient(1px 1px at 80% 20%, var(--c-accent), transparent),
    radial-gradient(1px 1px at 40% 80%, var(--c-secondary), transparent),
    radial-gradient(1px 1px at 70% 50%, var(--c-secondary), transparent);
  opacity: 0.2;
}

/* Emphasis marker — subtle left border highlight */
.emphasis-marker {
  position: absolute;
  left: 4vw;
  top: 50%;
  transform: translateY(-50%);
  width: 2px;
  height: 30%;
  background: linear-gradient(180deg, transparent, var(--c-accent), transparent);
  opacity: 0.3;
}

/* Pillar structure for recap */
.pillar-structure {
  position: absolute;
  top: 20%;
  bottom: 20%;
  width: 100%;
  pointer-events: none;
  z-index: 0;
  display: flex;
  justify-content: space-around;
}
.pillar-structure::before,
.pillar-structure::after {
  content: '';
  width: 1px;
  height: 100%;
  background: linear-gradient(180deg, transparent, rgba(0,0,0,0.06), transparent);
}

/* Pressure overlay for conflict */
.pressure-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(0,0,0,0.15) 100%);
  pointer-events: none;
  z-index: 0;
}

/* Intensity lines for escalation */
.intensity-lines {
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    repeating-linear-gradient(0deg, transparent, transparent 60px, rgba(255,255,255,0.02) 60px, rgba(255,255,255,0.02) 61px);
}

/* Soft gradient bg */
.subtle-gradient {
  background: linear-gradient(180deg, var(--c-bg) 0%, var(--c-surface-light) 100%);
}
"""


class ThemeEngine:
    """Cinematic surface system.

    Usage:
        engine = ThemeEngine(ds_colors)
        surface = engine.get_surface(narrative_role)
    """

    def __init__(self, ds_colors: dict):
        self.palette = derive_cinematic_palette(ds_colors)

    def get_surface(self, n_role: str) -> dict:
        """Get surface treatment for a narrative role."""
        return SURFACE_TREATMENTS.get(n_role, SURFACE_TREATMENTS["context"])

    def css_vars(self) -> str:
        """Generate CSS custom properties for the cinematic palette."""
        return "\n".join(f"    {k}: {v};" for k, v in self.palette.items())

    def ambient_css(self) -> str:
        """Get ambient effects CSS."""
        return AMBIENT_CSS

    def render_layers(self, layers: list[str]) -> str:
        """Generate HTML for depth layers."""
        html_parts = []
        for layer in layers:
            if layer == "ambient-glow":
                html_parts.append('<div class="glow-sphere top-right"></div>')
            elif layer == "accent-line":
                html_parts.append('<div class="accent-line top"></div>')
            elif layer == "tension-lines":
                html_parts.append('<div class="tension-lines"></div>')
            elif layer == "pressure-overlay":
                html_parts.append('<div class="pressure-overlay"></div>')
            elif layer == "rising-gradient":
                html_parts.append('<div class="rising-gradient"></div>')
            elif layer == "intensity-lines":
                html_parts.append('<div class="intensity-lines"></div>')
            elif layer == "glow-sphere":
                html_parts.append('<div class="glow-sphere center"></div>')
            elif layer == "accent-dust":
                html_parts.append('<div class="accent-dust"></div>')
            elif layer == "accent-wash":
                pass  # handled by background
            elif layer == "impact-ring":
                html_parts.append('<div class="impact-ring"></div>')
            elif layer == "pillar-structure":
                html_parts.append('<div class="pillar-structure"></div>')
            elif layer == "emphasis-marker":
                html_parts.append('<div class="emphasis-marker"></div>')
            elif layer == "surface-panel":
                html_parts.append('<div class="surface-panel"></div>')
        return "\n".join(html_parts)
