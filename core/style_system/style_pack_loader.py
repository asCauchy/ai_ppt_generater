"""Style Pack Loader — loads, validates, and caches style packs from JSON.

P5.5: Now supports family-qualified names.

Style packs can be addressed as:
  - 'apple_minimal'           (legacy flat, looks in styles root)
  - 'global_tech_cinematic/apple_glass'  (family-qualified)

The loader resolves family directories, validates packs against their
family manifests, and caches compiled StylePack instances.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Optional

from .style_schema import (
    StylePack, ColorSystem, TypographySystem, CompositionSystem,
    MotionLanguage, TransitionLanguage, SurfaceSystem, SpacingSystem,
    DensitySystem, EmphasisSystem, CinematicRhythm, EmotionalMapping,
)
from .inheritance_engine import InheritanceEngine
from .family_manager import FamilyManager


class StylePackLoader:
    """Load and cache style packs from disk. Supports family-qualified names."""

    def __init__(self, styles_root: str = None):
        if styles_root is None:
            styles_root = os.path.join(os.path.dirname(__file__), "..", "styles")
        self.styles_root = os.path.abspath(styles_root)
        self._cache: dict[str, StylePack] = {}
        self._inheritance = InheritanceEngine()
        self._family_mgr = FamilyManager(styles_root)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self, name: str) -> StylePack:
        """Load a style pack by name. Supports family-qualified names.

        'global_tech_cinematic/apple_glass' → family-scoped
        'apple_minimal' → legacy flat lookup
        """
        if name in self._cache:
            return self._cache[name]

        pack = self._load_raw(name)
        resolved = self._resolve(pack, name)
        self._cache[name] = resolved
        return resolved

    def list_packs(self) -> list[str]:
        """List all available style packs (family-qualified)."""
        return self._family_mgr.list_all_packs()

    def list_families(self) -> list[str]:
        """List all style families."""
        return self._family_mgr.discover_families()

    def list_packs_in_family(self, family_name: str) -> list[str]:
        """List packs within a specific family."""
        return self._family_mgr.list_packs_in_family(family_name)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _resolve_path(self, name: str) -> str:
        """Resolve a style pack name to a file path."""
        return self._family_mgr.get_pack_path(name)

    def _load_raw(self, name: str) -> dict:
        """Load raw JSON from a style pack."""
        path = self._resolve_path(name)
        if not os.path.isfile(path):
            # Try legacy flat lookup
            alt_path = os.path.join(self.styles_root, name, "style.json")
            if os.path.isfile(alt_path):
                path = alt_path
            else:
                raise FileNotFoundError(
                    f"Style pack not found: '{name}'. "
                    f"Tried: {path} and {alt_path}"
                )
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _resolve(self, raw: dict, lookup_name: str) -> StylePack:
        """Deserialize raw JSON into StylePack, resolving inheritance.

        Inheritance is restricted to within the SAME family.
        Cross-family inheritance is forbidden and will raise an error.
        """
        inherits = raw.get("inherits")
        if inherits:
            # Determine the family of this pack
            family = self._family_mgr.get_family_for_pack(lookup_name)

            # Validate: inheritance must be within the same family
            if "/" in str(inherits):
                parent_family = str(inherits).split("/")[0]
                if family and parent_family != family:
                    raise IsolationError(
                        f"Cross-family inheritance forbidden: '{lookup_name}' "
                        f"(family: {family}) cannot inherit from '{inherits}' "
                        f"(family: {parent_family})"
                    )
            else:
                # Unqualified parent name — check it's in the same family
                if family:
                    parent_in_family = os.path.join(
                        self.styles_root, family, str(inherits), "style.json"
                    )
                    if not os.path.isfile(parent_in_family):
                        raise IsolationError(
                            f"Parent pack '{inherits}' not found in family '{family}'. "
                            f"Cross-family inheritance is forbidden."
                        )

            parent = self.load(str(inherits))
            merged = self._inheritance.merge(parent, raw)
        else:
            merged = raw

        return self._dict_to_pack(merged)

    def _dict_to_pack(self, d: dict) -> StylePack:
        """Convert a resolved dict into a StylePack dataclass."""
        return StylePack(
            name=d.get("name", ""),
            version=d.get("version", "1.0"),
            description=d.get("description", ""),
            inherits=d.get("inherits"),
            color_system=self._dict_to_dataclass(d.get("color_system", {}), ColorSystem),
            typography_system=self._dict_to_dataclass(d.get("typography_system", {}), TypographySystem),
            composition_system=self._dict_to_dataclass(d.get("composition_system", {}), CompositionSystem),
            motion_language=self._dict_to_dataclass(d.get("motion_language", {}), MotionLanguage),
            transition_language=self._dict_to_dataclass(d.get("transition_language", {}), TransitionLanguage),
            surface_system=self._dict_to_dataclass(d.get("surface_system", {}), SurfaceSystem),
            spacing_system=self._dict_to_dataclass(d.get("spacing_system", {}), SpacingSystem),
            density_system=self._dict_to_dataclass(d.get("density_system", {}), DensitySystem),
            emphasis_system=self._dict_to_dataclass(d.get("emphasis_system", {}), EmphasisSystem),
            cinematic_rhythm=self._dict_to_dataclass(d.get("cinematic_rhythm", {}), CinematicRhythm),
            emotional_mapping=self._dict_to_dataclass(d.get("emotional_mapping", {}), EmotionalMapping),
            metadata=d.get("metadata", {}),
        )

    def _dict_to_dataclass(self, d: dict, cls):
        """Convert dict to dataclass instance, filling missing fields from defaults."""
        import dataclasses

        defaults = {}
        for f in dataclasses.fields(cls):
            if f.default is not dataclasses.MISSING:
                if isinstance(f.default, (int, float, str, bool, type(None))):
                    defaults[f.name] = f.default
                elif isinstance(f.default, dict):
                    defaults[f.name] = dict(f.default)
                elif isinstance(f.default, list):
                    defaults[f.name] = list(f.default)
            elif f.default_factory is not dataclasses.MISSING:
                defaults[f.name] = f.default_factory()

        kwargs = {}
        for f in dataclasses.fields(cls):
            if f.name in d:
                kwargs[f.name] = d[f.name]
            else:
                kwargs[f.name] = defaults.get(f.name)

        return cls(**kwargs)


class IsolationError(Exception):
    """Raised when a style pack violates family isolation rules."""
    pass
