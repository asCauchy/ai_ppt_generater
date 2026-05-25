"""Inheritance Engine — deep merge for style pack inheritance chains.

Style packs can inherit from parent packs:
  apple_minimal → apple_minimal_dark → apple_cinematic

The inheritance engine performs controlled deep merges:
  - Nested dicts are merged recursively
  - Lists are replaced (not appended) by child
  - Scalars are overridden by child
  - Parent values that aren't overridden are preserved

This avoids duplicating entire style definitions when only a few
values differ from the parent.
"""

from __future__ import annotations

import copy


class InheritanceEngine:
    """Resolves style pack inheritance chains via deep merge."""

    def merge(self, parent, child: dict) -> dict:
        """Merge child overrides onto parent. Child wins on conflict.

        parent can be a StylePack instance or a dict.
        Returns a plain dict.
        """
        if hasattr(parent, "__dataclass_fields__"):
            from dataclasses import asdict
            base = asdict(parent)
        else:
            base = copy.deepcopy(parent)

        return self._deep_merge(base, child)

    def merge_chain(self, packs: list) -> dict:
        """Merge a chain of packs in order. Later packs override earlier ones."""
        if not packs:
            return {}
        result = packs[0] if isinstance(packs[0], dict) else copy.deepcopy(packs[0])
        for pack in packs[1:]:
            result = self.merge(result, pack)
        return result

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _deep_merge(self, base: dict, overlay: dict) -> dict:
        """Recursive merge. overlay wins. Nested dicts are merged; everything else replaced."""
        result = copy.deepcopy(base)

        for key, value in overlay.items():
            if key not in result:
                result[key] = copy.deepcopy(value)
            elif isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = copy.deepcopy(value)

        return result
