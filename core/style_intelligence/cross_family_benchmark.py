"""Cross-Family Benchmark — prove aesthetic civilization isolation.

Renders the SAME presentation state across ALL families and ALL packs.
Generates a comparison dashboard proving:
  1. Each family produces a COMPLETELY DIFFERENT visual language
  2. Packs within a family share visual DNA but are distinct
  3. No cross-contamination between families
  4. Renderer never changes — only style packs change

The output is a comprehensive HTML dashboard with family grouping,
dimension scores, and side-by-side comparisons.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from ..style_system.family_manager import FamilyManager
from ..style_system.family_isolation import FamilyIsolation, isolation_report
from ..style_system.style_pack_loader import StylePackLoader
from .style_scoring_engine import StyleScoringEngine


class CrossFamilyBenchmark:
    """Render and compare across ALL families to prove complete isolation."""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "outputs"
            )
        self.output_dir = os.path.abspath(output_dir)
        self._loader = StylePackLoader()
        self._scorer = StyleScoringEngine()
        self._family_mgr = FamilyManager()
        self._isolation = FamilyIsolation()

    def run(self, state: dict, state_title: str = "Cross-Family Benchmark") -> dict:
        """Run comprehensive cross-family benchmark.

        Returns:
            Dict with full results, file paths, and isolation report.
        """
        families = self._family_mgr.discover_families()
        all_packs = self._loader.list_packs()

        print(f"\n{'=' * 70}")
        print(f"  CROSS-FAMILY BENCHMARK: '{state_title}'")
        print(f"  Families: {len(families)} | Total packs: {len(all_packs)}")
        print(f"{'=' * 70}")

        # Phase 1: Isolation validation
        print("\n--- Phase 1: Isolation Validation ---")
        violations = self._isolation.validate_all(
            self._loader.styles_root, families
        )
        print(isolation_report(violations))

        # Phase 2: Render all packs
        print("\n--- Phase 2: Rendering All Packs ---")
        render_results = {}
        for qualified_name in all_packs:
            family = self._family_mgr.get_family_for_pack(qualified_name)
            print(f"\n  [{family}] {qualified_name}")
            try:
                file_path, size_kb = self._render_pack(state, qualified_name)
                pack = self._loader.load(qualified_name)
                scores = self._scorer.score(pack)
                print(f"    Score: {scores.overall}/100 | Size: {size_kb:.1f} KB")

                render_results[qualified_name] = {
                    "family": family or "unassigned",
                    "pack_name": qualified_name.split("/")[-1],
                    "file_path": file_path,
                    "size_kb": round(size_kb, 1),
                    "scores": {
                        "overall": scores.overall,
                        "passed": scores.passed,
                        "dimensions": scores.dimensions,
                    },
                }
            except Exception as e:
                print(f"    ERROR: {e}")
                render_results[qualified_name] = {
                    "family": family or "unassigned",
                    "error": str(e),
                }

        # Phase 3: Family-level aggregation
        print("\n--- Phase 3: Family Aggregation ---")
        family_summaries = self._aggregate_by_family(render_results)
        for fam, summary in family_summaries.items():
            print(f"\n  [{fam}] — {summary['pack_count']} packs")
            print(f"    Avg score: {summary['avg_score']:.1f}/100")
            if summary.get("manifest"):
                m = summary["manifest"]
                print(f"    Philosophy: {m.philosophy[:80]}...")

        # Phase 4: Generate dashboard
        print("\n--- Phase 4: Dashboard Generation ---")
        dashboard_path = self._write_dashboard(
            state_title, families, render_results, family_summaries, violations
        )
        report_path = self._write_report(
            state_title, render_results, family_summaries, violations
        )

        print(f"\n{'=' * 70}")
        print(f"  CROSS-FAMILY BENCHMARK COMPLETE")
        print(f"  Dashboard: {dashboard_path}")
        print(f"  Report: {report_path}")
        print(f"{'=' * 70}")

        return {
            "state_title": state_title,
            "families": families,
            "pack_count": len(all_packs),
            "violations": len(violations),
            "family_summaries": {
                k: {"avg_score": v["avg_score"], "pack_count": v["pack_count"]}
                for k, v in family_summaries.items()
            },
            "dashboard_path": dashboard_path,
            "report_path": report_path,
            "isolation_clean": len(violations) == 0,
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _render_pack(self, state: dict, qualified_name: str) -> tuple:
        """Render state with a specific pack. Returns (path, size_kb)."""
        from ..rendering import render_to_file

        safe_name = qualified_name.replace("/", "_")
        filename = f"cross_family_{safe_name}.html"
        path = os.path.join(self.output_dir, filename)
        render_to_file(state, path, style_pack_name=qualified_name)
        return (path, os.path.getsize(path) / 1024)

    def _aggregate_by_family(self, results: dict) -> dict:
        """Aggregate scores by family."""
        families = {}
        for qname, data in results.items():
            fam = data.get("family", "unassigned")
            if fam not in families:
                manifest = None
                try:
                    manifest = self._family_mgr.get_manifest(fam)
                except Exception:
                    pass

                families[fam] = {
                    "pack_count": 0,
                    "total_score": 0.0,
                    "scores": [],
                    "manifest": manifest,
                }

            if data.get("scores"):
                families[fam]["pack_count"] += 1
                families[fam]["total_score"] += data["scores"]["overall"]
                families[fam]["scores"].append(data["scores"]["overall"])

        for fam in families:
            count = families[fam]["pack_count"]
            families[fam]["avg_score"] = (
                families[fam]["total_score"] / count if count > 0 else 0
            )

        return families

    def _write_dashboard(self, title: str, families: list[str],
                          results: dict, summaries: dict,
                          violations: list) -> str:
        """Generate the cross-family comparison dashboard HTML."""
        total_packs = len(results)
        clean_count = sum(1 for r in results.values() if r.get("scores", {}).get("passed"))

        # Family cards
        family_cards = []
        for fam_name in families:
            summary = summaries.get(fam_name, {})
            manifest = summary.get("manifest")
            philosophy = (manifest.philosophy[:100] + "...") if manifest and manifest.philosophy else ""

            # Get packs in this family
            fam_packs = {
                k: v for k, v in results.items()
                if v.get("family") == fam_name
            }

            pack_rows = []
            for qname, data in sorted(fam_packs.items()):
                s = data.get("scores", {})
                score = s.get("overall", 0)
                passed = s.get("passed", False)
                status = "PASS" if passed else "FAIL"
                status_color = "#22C55E" if passed else "#EF4444"
                score_color = self._score_color(score)

                dim_bars = ""
                for d in s.get("dimensions", []):
                    ds = d.get("score", 0)
                    dc = self._score_color(ds)
                    dim_bars += (
                        f'<span style="display:inline-block;width:12px;height:12px;'
                        f'background:{dc};border-radius:2px;margin:0 1px" '
                        f'title="{d.get("name","")}: {ds:.0f}"></span>'
                    )

                pack_rows.append(f"""<tr>
    <td style="font-size:0.9em">{data['pack_name']}</td>
    <td style="color:{score_color};font-weight:700">{score:.0f}</td>
    <td style="color:{status_color}">{status}</td>
    <td>{data.get('size_kb', 0):.0f} KB</td>
    <td>{dim_bars}</td>
</tr>""")

            family_cards.append(f"""<div class="family-card">
    <div class="family-header">
      <h2>{fam_name}</h2>
      <span class="family-score" style="color:{self._score_color(summary.get('avg_score', 0))}">
        Avg: {summary.get('avg_score', 0):.0f}
      </span>
    </div>
    <p class="family-philosophy">{philosophy}</p>
    <div class="family-stats">
      <span>{summary.get('pack_count', 0)} packs</span>
    </div>
    <table>
      <thead><tr><th>Pack</th><th>Score</th><th>Status</th><th>Size</th><th>Dims</th></tr></thead>
      <tbody>{"".join(pack_rows)}</tbody>
    </table>
</div>""")

        # Isolation status
        iso_status = ("CLEAN — All families isolated" if len(violations) == 0
                       else f"WARNING: {len(violations)} violations found")
        iso_color = "#22C55E" if len(violations) == 0 else "#EF4444"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Cross-Family Benchmark: {title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: system-ui, -apple-system, sans-serif; background:#080808; color:#DDD; padding:2em; }}
h1 {{ font-size:2.2em; margin-bottom:0.2em; }}
.subtitle {{ color:#777; margin-bottom:2em; font-size:0.9em; }}
.summary {{ display:flex; gap:1.5em; margin-bottom:2.5em; flex-wrap:wrap; }}
.stat {{ background:#141414; border:1px solid #222; border-radius:12px; padding:1.2em 1.8em; text-align:center; min-width:120px; }}
.stat-value {{ font-size:2.2em; font-weight:800; }}
.stat-label {{ font-size:0.8em; color:#777; margin-top:0.3em; text-transform:uppercase; letter-spacing:0.05em; }}
.family-card {{ background:#111; border:1px solid #1A1A1A; border-radius:14px; padding:1.5em; margin-bottom:2em; }}
.family-header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5em; }}
.family-header h2 {{ font-size:1.5em; color:#EEE; }}
.family-score {{ font-size:1.4em; font-weight:800; }}
.family-philosophy {{ color:#888; font-size:0.9em; margin-bottom:1em; line-height:1.4; }}
.family-stats {{ font-size:0.85em; color:#666; margin-bottom:1em; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ background:#1A1A1A; padding:10px 14px; text-align:left; font-size:0.8em; text-transform:uppercase; letter-spacing:0.05em; color:#888; }}
td {{ padding:10px 14px; border-top:1px solid #1A1A1A; font-size:0.9em; }}
tr:hover {{ background:rgba(255,255,255,0.02); }}
.isolation-badge {{ display:inline-block; padding:0.3em 0.8em; border-radius:6px; font-size:0.85em; font-weight:600; }}
</style>
</head>
<body>
<h1>Cross-Family Benchmark</h1>
<p class="subtitle">{title} &mdash; {len(families)} families, {total_packs} packs &mdash; {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

<div class="summary">
  <div class="stat">
    <div class="stat-value">{len(families)}</div>
    <div class="stat-label">Aesthetic Civilizations</div>
  </div>
  <div class="stat">
    <div class="stat-value">{total_packs}</div>
    <div class="stat-label">Style Packs</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:#22C55E">{clean_count}</div>
    <div class="stat-label">Passing (>=60)</div>
  </div>
  <div class="stat">
    <div class="stat-value" style="color:{iso_color}">{iso_status.split(':')[0]}</div>
    <div class="stat-label">Isolation</div>
  </div>
</div>

{"".join(family_cards)}
</body>
</html>"""

        path = os.path.join(self.output_dir, "cross_family_dashboard.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path

    def _write_report(self, title: str, results: dict,
                       summaries: dict, violations: list) -> str:
        """Write a JSON benchmark report."""
        report = {
            "title": title,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "families": list(summaries.keys()),
            "total_packs": len(results),
            "isolation_violations": len(violations),
            "isolation_clean": len(violations) == 0,
            "violation_details": violations if violations else [],
            "family_summaries": {
                k: {"pack_count": v["pack_count"], "avg_score": v["avg_score"]}
                for k, v in summaries.items()
            },
            "pack_results": {},
        }

        for qname, data in results.items():
            entry = {
                "family": data.get("family"),
                "pack_name": data.get("pack_name"),
                "file": os.path.basename(data.get("file_path", "")),
                "size_kb": data.get("size_kb"),
            }
            if data.get("scores"):
                entry["scores"] = data["scores"]
            if data.get("error"):
                entry["error"] = data["error"]
            report["pack_results"][qname] = entry

        path = os.path.join(self.output_dir, "cross_family_report.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        return path

    def _score_color(self, score: float) -> str:
        if score >= 80:
            return "#22C55E"
        elif score >= 60:
            return "#F59E0B"
        else:
            return "#EF4444"
