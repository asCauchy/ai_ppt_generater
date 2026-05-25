"""Style Resolver — SemanticRequirements + StylePack → ResolvedVisualConfig.

This is the central mapping engine of the Style OS. It takes:
  - SemanticRequirements (WHAT the slide needs — style-agnostic)
  - StylePack (the aesthetic rulebook)

And produces:
  - ResolvedVisualConfig (concrete CSS values for the renderer)

This replaces every hardcoded dict currently in html_renderer.py:
  SCENE_TEMPLATES, EMOTIONAL_MOTION, RELATION_TRANSITIONS,
  plus all the dicts in theme_engine, typography_engine, composition_engine.

The resolver makes ZERO aesthetic choices itself — it purely looks up values
defined in the StylePack.
"""

from __future__ import annotations

from .style_schema import (
    StylePack, SemanticRequirements, ResolvedVisualConfig,
    ColorSystem,
)

# Easing curve name → CSS value
EASING_CSS = {
    "default": "cubic-bezier(0.22, 0, 0, 1)",
    "emphatic": "cubic-bezier(0, 0.7, 0.3, 1)",
    "gentle": "cubic-bezier(0.4, 0, 0.2, 1)",
    "snappy": "cubic-bezier(0, 0, 0.2, 1)",
    "dramatic": "cubic-bezier(0.3, 0, 1, 1)",
}


class StyleResolver:
    """Resolve SemanticRequirements through a StylePack into concrete visual config."""

    def __init__(self, style_pack: StylePack):
        self.pack = style_pack

    # ------------------------------------------------------------------
    # Per-slide resolution
    # ------------------------------------------------------------------

    def resolve(self, req: SemanticRequirements, position: int, total: int) -> ResolvedVisualConfig:
        """Resolve visual config for a single slide from semantic requirements."""
        cfg = ResolvedVisualConfig()

        self._resolve_colors(cfg, req)
        self._resolve_typography(cfg, req)
        self._resolve_spacing(cfg, req)
        self._resolve_motion(cfg, req)
        self._resolve_transition(cfg, req)
        self._resolve_layout(cfg, req, position, total)
        self._resolve_surface(cfg, req)
        self._resolve_density(cfg, req)
        self._resolve_metadata(cfg, req)

        return cfg

    # ------------------------------------------------------------------
    # Sub-resolvers
    # ------------------------------------------------------------------

    def _resolve_colors(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        cs = self.pack.color_system
        ss = self.pack.surface_system
        n_role = req.narrative_role

        surface = ss.surfaces.get(n_role, ss.surfaces.get("context", {}))
        bg_key = surface.get("background", "surface_bg")
        text_key = surface.get("text_color", "text_primary")
        text_sec_key = surface.get("text_secondary", "text_tertiary")

        # Resolve semantic color names to concrete values
        cfg.bg_css = ss.background_css.get(bg_key, bg_key)
        cfg.text_color = self._get_color(cs, text_key)
        cfg.text_secondary_color = self._get_color(cs, text_sec_key)
        cfg.accent_color = cs.accent
        cfg.accent_glow = surface.get("accent_glow", False)

    def _resolve_typography(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        ts = self.pack.typography_system
        es = self.pack.emphasis_system
        n_role = req.narrative_role
        emphasis = req.emphasis_level

        # Get role prescription
        role_spec = ts.role_prescriptions.get(n_role, ts.role_prescriptions.get("context", {})).copy()

        # Apply emphasis modifiers
        if emphasis in es.level_modifiers:
            scale_up = es.level_modifiers[emphasis].get("title_scale_up", {})
            current_scale = role_spec.get("title_scale", "h1")
            role_spec["title_scale"] = scale_up.get(current_scale, current_scale)

        # Intensity affects body scale
        intensity = req.intensity
        body_scale_map = {1: "body_sm", 2: "body_sm", 3: "body", 4: "body_lg", 5: "body_lg"}
        role_spec["body_scale"] = body_scale_map.get(intensity, "body")

        # Resolve scale names to px values
        scale_map = {
            "micro": ts.scale_micro, "caption": ts.scale_caption,
            "body_sm": ts.scale_body_sm, "body": ts.scale_body,
            "body_lg": ts.scale_body_lg, "h3": ts.scale_h3, "h2": ts.scale_h2,
            "h1": ts.scale_h1, "hero": ts.scale_hero,
            "display": ts.scale_display, "mega": ts.scale_mega,
        }

        cfg.title_size_px = scale_map.get(role_spec.get("title_scale", "h1"), 36)
        cfg.title_weight = role_spec.get("title_weight", 600)
        cfg.title_tracking_em = role_spec.get("title_tracking", -0.01)
        cfg.subtitle_size_px = scale_map.get(role_spec.get("subtitle_scale", "body_lg"), 18)
        cfg.body_size_px = scale_map.get(role_spec.get("body_scale", "body"), 16)
        cfg.body_weight = role_spec.get("body_weight", 400)
        cfg.line_height_title = role_spec.get("line_height_title", 1.15)
        cfg.line_height_body = role_spec.get("line_height_body", 1.5)
        cfg.max_width_ch = role_spec.get("max_width_ch", 55)
        cfg.word_limit = role_spec.get("word_limit", 30)
        cfg.whitespace_ratio = role_spec.get("whitespace_ratio", 0.25)
        cfg.vertical_align = role_spec.get("vertical_align", "top")

        # Font families
        cfg.title_font = ts.title_font
        cfg.body_font = ts.body_font

    def _resolve_spacing(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        sp = self.pack.spacing_system
        cs = self.pack.composition_system
        n_role = req.narrative_role

        # Negative space affects padding
        neg = cs.negative_space.get(n_role, 0.25)
        pad_v = f"{max(2, 4 * (0.5 + neg * 3)):.0f}vh"
        pad_h = f"{max(2, 6 - neg * 4):.0f}vw"
        cfg.slide_padding = f"{pad_v} {pad_h}"

        cfg.content_gap = sp.content_gap
        cfg.title_margin_bottom = sp.title_margin_bottom

    def _resolve_motion(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        ml = self.pack.motion_language
        em = self.pack.emotional_mapping
        e_role = req.emotional_role
        intensity = req.intensity

        # Entrance from emotional role
        entrance_spec = ml.emotional_entrance.get(e_role, ml.emotional_entrance.get("engaged", {}))
        cfg.entrance_type = entrance_spec.get("type", "active_reveal")
        cfg.scale_variation = entrance_spec.get("scale_var", 0)

        # Easing
        easing_name = entrance_spec.get("easing", "default")
        cfg.easing_curve = EASING_CSS.get(easing_name, EASING_CSS["default"])

        # Stagger and duration from intensity
        base_stagger = entrance_spec.get("stagger_ms", 150)
        intensity_mod = ml.intensity_speed.get(intensity, ml.intensity_speed.get(3, {}))
        cfg.stagger_ms = int(base_stagger * intensity_mod.get("stagger_mult", 1.0))
        cfg.duration_ms = int(400 * intensity_mod.get("duration_mult", 0.7))

        # Kinetic typography
        kinetic = em.kinetic_typography.get(e_role, {})
        cfg.emphasis_delay = kinetic.get("emphasis_delay", 0.4)
        cfg.weight_keywords = kinetic.get("weight_keywords", False)

    def _resolve_transition(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        tl = self.pack.transition_language
        rel = req.relation_to_next

        trans_spec = tl.relation_transitions.get(rel, tl.relation_transitions.get("progression", {}))
        cfg.transition_type = trans_spec.get("type", tl.default_transition)
        cfg.transition_duration_ms = trans_spec.get("duration_ms", tl.default_duration_ms)
        cfg.transition_easing = trans_spec.get("easing", tl.default_easing)

    def _resolve_layout(self, cfg: ResolvedVisualConfig, req: SemanticRequirements,
                         position: int, total: int):
        cs = self.pack.composition_system
        n_role = req.narrative_role

        cfg.container_class = cs.container_class.get(n_role, "overview_grid")
        cfg.asymmetry = cs.asymmetry.get(n_role, "balanced")

        # Grid template
        asym = cfg.asymmetry
        if asym == "dynamic_shift":
            asym = "slight_left" if position % 2 == 0 else "balanced"
        grid = cs.grid_templates.get(asym, "1fr")
        cfg.grid_template_columns = grid

        # Grid areas
        if grid == "1fr":
            cfg.grid_template_areas = '"content"'
        elif grid == "1fr min(1100px, 90vw) 1fr":
            cfg.grid_template_areas = '". content ."'
        else:
            cfg.grid_template_areas = '"content side"'

        # Layout mode
        is_split = n_role in ("conflict", "evidence", "escalation") or grid not in ("1fr",)
        cfg.is_split_layout = is_split
        cfg.content_layout_mode = "centered" if asym == "symmetric" else "split"

    def _resolve_surface(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        ss = self.pack.surface_system
        cs = self.pack.composition_system
        n_role = req.narrative_role

        # Depth layers → HTML fragments
        layers = cs.depth_layers.get(n_role, [])
        ambient_parts = []
        for layer in layers:
            fragment = self._layer_html(layer)
            if fragment:
                ambient_parts.append(fragment)

        cfg.ambient_html = "\n".join(ambient_parts)

        # Surface ambient class
        surface = ss.surfaces.get(n_role, {})
        has_ambient = surface.get("ambient", "none")
        cfg.ambient_css_class = "has-ambient" if has_ambient == "glow" else ""

    def _resolve_density(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        ds = self.pack.density_system
        intensity = req.intensity
        level = ds.levels.get(intensity, ds.levels.get(3, {}))
        cfg.max_points = level.get("max_points", 4)
        cfg.max_chars_per_point = level.get("max_chars_per_point", 80)

    def _resolve_metadata(self, cfg: ResolvedVisualConfig, req: SemanticRequirements):
        cfg.narrative_role = req.narrative_role
        cfg.intensity = req.intensity
        cfg.pace = req.pace
        cfg.emphasis_level = req.emphasis_level
        cfg.act = req.act

    # ------------------------------------------------------------------
    # Bulk resolution — all requirements
    # ------------------------------------------------------------------

    def resolve_all(self, requirements: list[SemanticRequirements]) -> list[ResolvedVisualConfig]:
        """Resolve visual configs for multiple semantic requirements in one pass."""
        total = len(requirements)
        return [self.resolve(req, i, total) for i, req in enumerate(requirements)]

    # ------------------------------------------------------------------
    # Color helpers
    # ------------------------------------------------------------------

    def _get_color(self, cs: ColorSystem, semantic_name: str) -> str:
        """Resolve a semantic color name to a concrete CSS value."""
        mapping = {
            "text_on_brand": cs.text_on_brand,
            "text_on_brand_secondary": cs.text_on_brand_secondary,
            "text_primary": cs.text_primary,
            "text_secondary": cs.text_secondary,
            "text_tertiary": cs.text_tertiary,
            "text_on_dark": cs.text_on_dark,
            "text_on_dark_secondary": cs.text_on_dark_secondary,
            "surface_bg": cs.surface_bg,
        }
        return mapping.get(semantic_name, cs.text_primary)

    def _layer_html(self, layer_name: str) -> str:
        """Generate HTML for a depth layer. Style-swappable surface elements."""
        fragments = {
            "ambient_glow": '<div class="glow-sphere top-right"></div>',
            "accent_line": '<div class="accent-line top"></div>',
            "tension_lines": '<div class="tension-lines"></div>',
            "pressure_overlay": '<div class="pressure-overlay"></div>',
            "rising_gradient": '<div class="rising-gradient"></div>',
            "intensity_lines": '<div class="intensity-lines"></div>',
            "glow_sphere": '<div class="glow-sphere center"></div>',
            "accent_dust": '<div class="accent-dust"></div>',
            "impact_ring": '<div class="impact-ring"></div>',
            "pillar_structure": '<div class="pillar-structure"></div>',
            "emphasis_marker": '<div class="emphasis-marker"></div>',
            "surface_panel": '<div class="surface-panel"></div>',
        }
        return fragments.get(layer_name, "")

    # ------------------------------------------------------------------
    # CSS tokens — design system → CSS custom properties
    # ------------------------------------------------------------------

    def css_tokens(self) -> str:
        """Generate CSS custom properties for the entire style pack.
        These are the :root { ... } variables that the renderer uses.
        """
        cs = self.pack.color_system
        ts = self.pack.typography_system
        sp = self.pack.spacing_system
        ss = self.pack.surface_system
        ml = self.pack.motion_language

        lines = []

        # Colors
        color_vars = [
            ("--c-primary", cs.primary),
            ("--c-primary-light", cs.primary_light),
            ("--c-primary-dark", cs.primary_dark),
            ("--c-accent", cs.accent),
            ("--c-accent-light", cs.accent_light),
            ("--c-accent-dark", cs.accent_dark),
            ("--c-surface-bg", cs.surface_bg),
            ("--c-surface-neutral", cs.surface_neutral),
            ("--c-surface-dark", cs.surface_dark),
            ("--c-surface-mid", cs.surface_mid),
            ("--c-surface-glass", cs.surface_glass),
            ("--c-surface-raised", cs.surface_raised),
            ("--c-text-primary", cs.text_primary),
            ("--c-text-secondary", cs.text_secondary),
            ("--c-text-tertiary", cs.text_tertiary),
            ("--c-text-on-dark", cs.text_on_dark),
            ("--c-text-on-dark-secondary", cs.text_on_dark_secondary),
            ("--c-text-on-brand", cs.text_on_brand),
            ("--c-text-on-brand-secondary", cs.text_on_brand_secondary),
            ("--c-glow", cs.glow),
            ("--c-shadow", cs.shadow),
            ("--c-success", cs.success),
            ("--c-warning", cs.warning),
            ("--c-danger", cs.danger),
            ("--c-info", cs.info),
        ]
        for name, value in color_vars:
            lines.append(f"  {name}: {value};")

        # Typography scale
        scale_vars = [
            ("--font-micro", ts.scale_micro),
            ("--font-caption", ts.scale_caption),
            ("--font-body-sm", ts.scale_body_sm),
            ("--font-body", ts.scale_body),
            ("--font-body-lg", ts.scale_body_lg),
            ("--font-h3", ts.scale_h3),
            ("--font-h2", ts.scale_h2),
            ("--font-h1", ts.scale_h1),
            ("--font-hero", ts.scale_hero),
            ("--font-display", ts.scale_display),
            ("--font-mega", ts.scale_mega),
        ]
        for name, value in scale_vars:
            lines.append(f"  {name}: {value}px;")

        # Font families
        lines.append(f"  --font-title: '{ts.title_font}';")
        lines.append(f"  --font-body: '{ts.body_font}';")
        lines.append(f"  --font-mono: '{ts.mono_font}';")

        # Spacing
        lines.append(f"  --spacing-unit: {sp.unit_px}px;")
        lines.append(f"  --radius: 12px;")
        lines.append(f"  --transition-speed: {ml.intensity_speed.get(3, {}).get('duration_mult', 0.7) * 400:.0f}ms;")
        lines.append(f"  --transition-easing: {ml.default_easing};")

        # Easing curves
        for name, css in EASING_CSS.items():
            lines.append(f"  --easing-{name}: {css};")

        return "\n".join(lines)


def create_resolver(style_pack: StylePack) -> StyleResolver:
    """Factory function for StyleResolver."""
    return StyleResolver(style_pack)
