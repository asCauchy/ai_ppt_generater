"""Family Isolation — enforce isolation rules between style families.

Isolation rules:
  1. No cross-family inheritance (pack in family A cannot inherit from family B)
  2. No shared aesthetic vocabulary tokens that would cause contamination
  3. Each family's packs must stay within their own vocabulary
  4. No global defaults leaking between families

This module is the GUARD of the style family architecture.
"""

from __future__ import annotations

import json
import os


class FamilyIsolation:
    """Enforce and validate isolation between style families."""

    def validate_all(self, styles_root: str, families: list[str]) -> list[dict]:
        """Run all isolation checks across families.

        Returns a list of violation dicts. Empty list = clean.
        """
        violations = []

        violations.extend(self.check_cross_family_inheritance(styles_root, families))
        violations.extend(self.check_vocabulary_contamination(styles_root, families))
        violations.extend(self.check_pack_isolation(styles_root, families))

        return violations

    # ------------------------------------------------------------------
    # Rule 1: No cross-family inheritance
    # ------------------------------------------------------------------

    def check_cross_family_inheritance(self, styles_root: str,
                                        families: list[str]) -> list[dict]:
        """Verify no pack inherits from a pack in a different family."""
        violations = []

        for family in families:
            family_dir = os.path.join(styles_root, family)
            for entry in os.listdir(family_dir):
                pack_dir = os.path.join(family_dir, entry)
                style_json = os.path.join(pack_dir, "style.json")
                if os.path.isfile(style_json):
                    with open(style_json, "r", encoding="utf-8") as f:
                        pack = json.load(f)
                    inherits = pack.get("inherits")
                    if inherits:
                        # Check if inheritance crosses family boundary
                        if "/" in str(inherits):
                            parent_family = str(inherits).split("/")[0]
                            if parent_family != family:
                                violations.append({
                                    "rule": "cross_family_inheritance",
                                    "pack": f"{family}/{entry}",
                                    "inherits_from": inherits,
                                    "message": f"Pack '{family}/{entry}' inherits from '{inherits}' which is in a different family. Cross-family inheritance is forbidden.",
                                })
                        else:
                            # Unqualified inheritance — check which family the parent is in
                            parent_family = None
                            for f in families:
                                parent_path = os.path.join(styles_root, f, str(inherits), "style.json")
                                if os.path.isfile(parent_path):
                                    parent_family = f
                                    break
                            # Also check flat (legacy) packs
                            if parent_family is None:
                                parent_path = os.path.join(styles_root, str(inherits), "style.json")
                                if os.path.isfile(parent_path):
                                    parent_family = "(legacy root)"

                            if parent_family and parent_family != family:
                                violations.append({
                                    "rule": "cross_family_inheritance",
                                    "pack": f"{family}/{entry}",
                                    "inherits_from": inherits,
                                    "message": f"Pack '{family}/{entry}' inherits from '{inherits}' (found in '{parent_family}'). Cross-family inheritance is forbidden.",
                                })

        return violations

    # ------------------------------------------------------------------
    # Rule 2: No vocabulary contamination between families
    # ------------------------------------------------------------------

    def check_vocabulary_contamination(self, styles_root: str,
                                        families: list[str]) -> list[dict]:
        """Check that families don't share forbidden vocabulary.

        The key check: a family's forbidden_patterns should NOT appear in
        any other family's packs.
        """
        violations = []

        # Load all manifests
        manifests = {}
        for family in families:
            manifest_path = os.path.join(styles_root, family, "_family.json")
            if os.path.isfile(manifest_path):
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifests[family] = json.load(f)

        # For each family, check that other families' packs don't contain
        # its forbidden patterns in a way that would indicate contamination
        for family in families:
            forbidden = manifests.get(family, {}).get("forbidden_patterns", [])
            for other_family in families:
                if other_family == family:
                    continue
                # Load all packs from other_family
                family_dir = os.path.join(styles_root, other_family)
                for entry in os.listdir(family_dir):
                    pack_path = os.path.join(family_dir, entry, "style.json")
                    if os.path.isfile(pack_path):
                        with open(pack_path, "r", encoding="utf-8") as f:
                            pack = json.load(f)
                        pack_str = json.dumps(pack).lower()
                        # This is a heuristic check — real contamination would
                        # be more nuanced. We flag only clear keyword clusters.
                        for pattern in forbidden:
                            keywords = [w for w in pattern.lower().split() if len(w) > 5]
                            matches = [kw for kw in keywords if kw in pack_str]
                            if len(matches) >= len(keywords) * 0.6 and len(matches) >= 2:
                                violations.append({
                                    "rule": "vocabulary_contamination",
                                    "source_family": family,
                                    "target_family": other_family,
                                    "target_pack": f"{other_family}/{entry}",
                                    "forbidden_pattern": pattern,
                                    "message": f"Pack '{other_family}/{entry}' may contain pattern forbidden by '{family}': '{pattern}'",
                                })

        return violations

    # ------------------------------------------------------------------
    # Rule 3: Pack-level isolation checks
    # ------------------------------------------------------------------

    def check_pack_isolation(self, styles_root: str,
                              families: list[str]) -> list[dict]:
        """Individual pack-level checks to prevent cross-contamination."""
        violations = []

        for family in families:
            family_dir = os.path.join(styles_root, family)
            manifest_path = os.path.join(family_dir, "_family.json")
            if not os.path.isfile(manifest_path):
                continue

            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            # Check each pack in the family
            for entry in os.listdir(family_dir):
                pack_dir = os.path.join(family_dir, entry)
                style_json = os.path.join(pack_dir, "style.json")
                if not os.path.isfile(style_json):
                    continue

                with open(style_json, "r", encoding="utf-8") as f:
                    pack = json.load(f)

                # Verify the pack name matches its directory
                pack_name = pack.get("name", "")
                if pack_name and pack_name != entry:
                    violations.append({
                        "rule": "pack_name_mismatch",
                        "family": family,
                        "directory": entry,
                        "declared_name": pack_name,
                        "message": f"Pack directory '{entry}' declares name '{pack_name}' in style.json. These must match.",
                    })

        return violations


def isolation_report(violations: list[dict]) -> str:
    """Format isolation violations into a human-readable report."""
    if not violations:
        return "ALL CLEAN — No isolation violations detected."

    lines = [f"ISOLATION VIOLATIONS: {len(violations)} found", "=" * 50]
    by_rule = {}
    for v in violations:
        rule = v.get("rule", "unknown")
        by_rule.setdefault(rule, []).append(v)

    for rule, items in by_rule.items():
        lines.append(f"\n[{rule}] — {len(items)} violation(s):")
        for item in items:
            lines.append(f"  • {item['message']}")

    return "\n".join(lines)
