"""Family Manager — discover, validate, and manage style families.

The manager:
  1. Discovers all families under the styles root
  2. Loads and validates family manifests
  3. Lists packs within a family
  4. Validates that packs conform to family vocabulary
  5. Enforces family-level isolation rules
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from typing import Optional

from .family_manifest import FamilyManifest
from .family_isolation import FamilyIsolation


class FamilyManager:
    """Manage style families — discovery, validation, and pack listing."""

    def __init__(self, styles_root: str = None):
        if styles_root is None:
            styles_root = os.path.join(os.path.dirname(__file__), "..", "styles")
        self.styles_root = os.path.abspath(styles_root)
        self._manifests: dict[str, FamilyManifest] = {}
        self._isolation = FamilyIsolation()

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_families(self) -> list[str]:
        """Discover all family directories."""
        families = []
        if not os.path.isdir(self.styles_root):
            return families
        for entry in sorted(os.listdir(self.styles_root)):
            family_dir = os.path.join(self.styles_root, entry)
            manifest_path = os.path.join(family_dir, "_family.json")
            if os.path.isdir(family_dir) and os.path.isfile(manifest_path):
                families.append(entry)
        return families

    def get_manifest(self, family_name: str) -> FamilyManifest:
        """Load a family manifest from disk. Cached after first load."""
        if family_name in self._manifests:
            return self._manifests[family_name]

        family_dir = os.path.join(self.styles_root, family_name)
        manifest_path = os.path.join(family_dir, "_family.json")

        if not os.path.isfile(manifest_path):
            raise FileNotFoundError(
                f"Family '{family_name}' not found at {manifest_path}"
            )

        with open(manifest_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        manifest = FamilyManifest.from_dict(data)
        self._manifests[family_name] = manifest
        return manifest

    # ------------------------------------------------------------------
    # Pack listing (family-scoped)
    # ------------------------------------------------------------------

    def list_packs_in_family(self, family_name: str) -> list[str]:
        """List all style packs within a family directory.

        Returns pack names WITHOUT the family prefix.
        """
        family_dir = os.path.join(self.styles_root, family_name)
        if not os.path.isdir(family_dir):
            return []

        packs = []
        for entry in sorted(os.listdir(family_dir)):
            pack_dir = os.path.join(family_dir, entry)
            style_json = os.path.join(pack_dir, "style.json")
            if os.path.isdir(pack_dir) and os.path.isfile(style_json):
                packs.append(entry)
        return packs

    def list_all_packs(self) -> list[str]:
        """List all packs across all families.

        Returns family-qualified names: 'global_tech_cinematic/apple_glass'
        """
        all_packs = []
        for family in self.discover_families():
            for pack in self.list_packs_in_family(family):
                all_packs.append(f"{family}/{pack}")
        # Also check for legacy flat packs at root level
        for entry in sorted(os.listdir(self.styles_root)):
            pack_path = os.path.join(self.styles_root, entry)
            style_json = os.path.join(pack_path, "style.json")
            if os.path.isdir(pack_path) and os.path.isfile(style_json):
                # It's a pack directory, not a family (no _family.json)
                manifest = os.path.join(pack_path, "_family.json")
                if not os.path.isfile(manifest):
                    if entry not in [p.split("/")[0] for p in all_packs]:
                        all_packs.append(entry)
        return sorted(all_packs)

    def get_family_for_pack(self, pack_name: str) -> Optional[str]:
        """Find which family a pack belongs to."""
        if "/" in pack_name:
            return pack_name.split("/")[0]

        # Search all families for this pack
        for family in self.discover_families():
            if pack_name in self.list_packs_in_family(family):
                return family
        return None

    def get_pack_path(self, qualified_name: str) -> str:
        """Resolve a qualified pack name to a file path.

        'global_tech_cinematic/apple_glass' → '...styles/global_tech_cinematic/apple_glass/style.json'
        'apple_minimal' (legacy flat) → '...styles/apple_minimal/style.json'
        """
        if "/" in qualified_name:
            family, pack = qualified_name.split("/", 1)
            return os.path.join(self.styles_root, family, pack, "style.json")
        else:
            return os.path.join(self.styles_root, qualified_name, "style.json")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate_pack_against_family(self, pack: dict, family_name: str) -> list[str]:
        """Validate that a style pack conforms to its family's vocabulary.

        Checks concrete aesthetic fields in the pack against the family's
        forbidden_patterns. Returns a list of violations (empty = valid).
        """
        manifest = self.get_manifest(family_name)
        violations = []

        # Check concrete aesthetic signals against forbidden keywords
        # rather than naive string matching over the entire pack JSON.
        vocab = manifest.aesthetic_vocabulary
        forbidden_keywords = set()
        for pattern in manifest.forbidden_patterns:
            for word in pattern.lower().split():
                if len(word) > 4:
                    forbidden_keywords.add(word)

        # Check typography
        ts = pack.get("typography_system", {})
        title_font = ts.get("title_font", "").lower()
        body_font = ts.get("body_font", "").lower()
        if "serif" in forbidden_keywords:
            if "serif" in title_font and "sans" not in title_font:
                violations.append("Serif title font in sans-dominant family")
            if "serif" in body_font and "sans" not in body_font:
                violations.append("Serif body font in sans-dominant family")

        # Check surfaces
        ss = pack.get("surface_system", {})
        surfaces_data = json.dumps(ss).lower()
        if "gradient" in forbidden_keywords:
            bg_count = len(ss.get("background_css", {}))
            gradient_count = sum(1 for v in ss.get("background_css", {}).values()
                                if "gradient" in str(v).lower())
            if gradient_count > bg_count * 0.6:
                violations.append("Too many gradients for non-gradient family")

        return violations

    def validate_cross_family_isolation(self) -> list[dict]:
        """Check all families for cross-contamination.

        Returns list of isolation violations.
        """
        return self._isolation.validate_all(self.styles_root, self.discover_families())

    # ------------------------------------------------------------------
    # Family creation helper
    # ------------------------------------------------------------------

    def create_family(self, manifest: FamilyManifest) -> str:
        """Create a new family directory with manifest."""
        family_dir = os.path.join(self.styles_root, manifest.family_name)

        # Reject if already exists
        if os.path.exists(family_dir):
            raise FileExistsError(f"Family already exists: {manifest.family_name}")

        # Create directory structure
        for sub in ["references/raw", "references/selected", "references/distilled",
                     "analysis", "outputs"]:
            os.makedirs(os.path.join(family_dir, sub), exist_ok=True)

        # Write manifest
        manifest_path = os.path.join(family_dir, "_family.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest.to_dict(), f, indent=2, ensure_ascii=False)

        return family_dir
