"""Benchmark Renderer — multi-style comparison rendering.

Renders the same presentation state across multiple style packs and
produces:
  1. Individual HTML demo files for each style
  2. A comparison index HTML with side-by-side scores
  3. A benchmark JSON report with dimension-level scores

This is the final verification stage of the style intelligence pipeline.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

from .aesthetic_models import BenchmarkReport
from .style_scoring_engine import StyleScoringEngine


class BenchmarkRenderer:
    """Render and compare multiple style packs against the same state."""

    def __init__(self, output_dir: str = None):
        if output_dir is None:
            output_dir = os.path.join(
                os.path.dirname(__file__), "..", "..", "outputs"
            )
        self.output_dir = os.path.abspath(output_dir)
        self.scorer = StyleScoringEngine()

    def run(self, state: dict, style_names: list[str] = None,
            state_title: str = "Benchmark") -> BenchmarkReport:
        """Run benchmark across style packs.

        Args:
            state: Presentation state dict
            style_names: List of style pack names (None = all available)
            state_title: Title for the report

        Returns:
            BenchmarkReport with all results
        """
        # Discover style packs
        if style_names is None:
            from ..style_system.style_pack_loader import StylePackLoader
            loader = StylePackLoader()
            style_names = loader.list_packs()

        if not style_names:
            raise ValueError("No style packs found for benchmarking")

        print(f"\n{'=' * 60}")
        print(f"  Style Benchmark: '{state_title}'")
        print(f"  Comparing {len(style_names)} style packs")
        print(f"{'=' * 60}")

        results = []

        for style_name in style_names:
            print(f"\n--- {style_name} ---")

            # Render
            file_path, size_kb = self._render_state(state, style_name)

            # Score
            try:
                from ..style_system.style_pack_loader import StylePackLoader
                loader = StylePackLoader()
                pack = loader.load(style_name)
                scores = self.scorer.score(pack)
                print(f"  Score: {scores.overall}/100 {'PASS' if scores.passed else 'FAIL'}")
                for dim in scores.dimensions:
                    print(f"    {dim['name']}: {dim['score']:.0f}")
            except Exception as e:
                print(f"  Scoring error: {e}")
                scores = None

            results.append({
                "style_name": style_name,
                "file_path": file_path,
                "size_kb": round(size_kb, 1),
                "scores": {
                    "overall": scores.overall if scores else 0,
                    "passed": scores.passed if scores else False,
                    "dimensions": scores.dimensions if scores else [],
                } if scores else None,
            })

        # Generate comparison index
        index_path = self._write_comparison_index(state_title, results)

        # Generate JSON report
        report_path = self._write_report(state_title, results)

        report = BenchmarkReport(
            state_title=state_title,
            style_results=results,
            comparison_notes=f"Index: {index_path}\nReport: {report_path}",
            generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )

        # Print summary
        print(f"\n{'=' * 60}")
        print(f"  Benchmark Complete")
        print(f"  Index: {index_path}")
        print(f"  Report: {report_path}")
        print(f"{'=' * 60}")

        return report

    def _render_state(self, state: dict, style_name: str) -> tuple:
        """Render state with a style pack. Returns (path, size_kb)."""
        from ..rendering import render_to_file

        safe_name = style_name.replace("/", "_").replace("\\", "_")
        filename = f"benchmark_{safe_name}.html"
        path = os.path.join(self.output_dir, filename)

        render_to_file(state, path, style_pack_name=style_name)
        size_kb = os.path.getsize(path) / 1024
        print(f"  Rendered: {filename} ({size_kb:.1f} KB)")

        return (path, size_kb)

    def _write_comparison_index(self, title: str, results: list) -> str:
        """Write a comparison HTML index showing all benchmark results."""
        rows = []
        for r in results:
            scores = r.get("scores", {})
            overall = scores.get("overall", 0) if scores else 0
            passed = scores.get("passed", False) if scores else False
            dims = scores.get("dimensions", []) if scores else []

            dim_cells = ""
            for d in dims:
                color = self._score_color(d.get("score", 0))
                dim_cells += (
                    f'<td style="color:{color};font-size:0.85em">'
                    f'{d.get("name", "?").replace("_", " ").title()[:20]}<br>'
                    f'<strong>{d.get("score", 0):.0f}</strong></td>'
                )

            status = '<span style="color:#22C55E">PASS</span>' if passed else '<span style="color:#EF4444">FAIL</span>'
            score_color = self._score_color(overall)

            filename = f"benchmark_{r['style_name']}.html"

            rows.append(f"""<tr>
    <td><a href="{filename}">{r['style_name']}</a></td>
    <td style="color:{score_color};font-weight:700;font-size:1.2em">{overall:.0f}</td>
    <td>{status}</td>
    <td>{r['size_kb']:.0f} KB</td>
    {dim_cells}
</tr>""")

        # Dimension headers
        dim_headers = ""
        if results and results[0].get("scores", {}).get("dimensions"):
            for d in results[0]["scores"]["dimensions"]:
                dim_headers += f'<th>{d.get("name", "?").replace("_", " ").title()[:15]}</th>'

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Style Benchmark: {title}</title>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family: system-ui, -apple-system, sans-serif; background:#0A0A0A; color:#E0E0E0; padding:2em; }}
h1 {{ font-size:2em; margin-bottom:0.3em; }}
.subtitle {{ color:#888; margin-bottom:2em; }}
table {{ width:100%; border-collapse:collapse; background:#1A1A1A; border-radius:12px; overflow:hidden; }}
th {{ background:#2A2A2A; padding:12px 16px; text-align:left; font-size:0.85em; text-transform:uppercase; letter-spacing:0.05em; color:#AAA; }}
td {{ padding:12px 16px; border-top:1px solid #2A2A2A; }}
tr:hover {{ background:rgba(255,255,255,0.03); }}
a {{ color:#40A9FF; text-decoration:none; }}
a:hover {{ text-decoration:underline; }}
.summary {{ display:flex; gap:2em; margin-bottom:2em; }}
.stat {{ background:#1A1A1A; border-radius:12px; padding:1.5em 2em; text-align:center; }}
.stat-value {{ font-size:2.5em; font-weight:800; }}
.stat-label {{ font-size:0.85em; color:#888; margin-top:0.3em; }}
</style>
</head>
<body>
<h1>Style Benchmark</h1>
<p class="subtitle">{title} &mdash; {len(results)} style packs compared &mdash; {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}</p>

<div class="summary">
  <div class="stat">
    <div class="stat-value">{len(results)}</div>
    <div class="stat-label">Style Packs</div>
  </div>
  <div class="stat">
    <div class="stat-value">{sum(1 for r in results if r.get('scores', {}).get('passed', False) if r.get('scores'))}</div>
    <div class="stat-label">Passed (≥60)</div>
  </div>
</div>

<table>
<thead>
<tr>
  <th>Style Pack</th>
  <th>Overall</th>
  <th>Status</th>
  <th>Size</th>
  {dim_headers}
</tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
</body>
</html>"""

        path = os.path.join(self.output_dir, "benchmark_index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path

    def _write_report(self, title: str, results: list) -> str:
        """Write a JSON benchmark report."""
        report = {
            "title": title,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "style_count": len(results),
            "results": [],
        }

        for r in results:
            entry = {
                "style_name": r["style_name"],
                "file": os.path.basename(r["file_path"]),
                "size_kb": r["size_kb"],
            }
            if r.get("scores"):
                entry["scores"] = r["scores"]
            report["results"].append(entry)

        path = os.path.join(self.output_dir, "benchmark_report.json")
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
