"""P1 Convergence Benchmark — 10 runs, fixed input, measure semantic feedback loop.

Usage: python tools/run_p1_benchmark.py

Runs the pipeline 10 times with identical input, capturing retry behavior,
warning deltas, and semantic repair rates.
"""

import json, os, sys, time, shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import PresentationPipeline
from core.validator import PresentationValidator
from core.state_manager import init_presentation_state
from core.debug_snapshot import DebugSnapshot


SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH_DIR = os.path.join(SCRIPT_DIR, "debug", "p1_benchmark")

# Fixed input
TOPIC = "中国 AI 产业发展"
STYLE = "未来科技风"
PAGES = 7
CONTEXT = {
    "audience": {"profile": "科技行业从业者与投资人", "knowledge_level": "expert"},
    "occasion": {"type": "conference_keynote", "formality": "semi_formal"},
    "intent": {"primary_goal": "inspire", "desired_outcome": "激发听众对中国AI产业的信心与参与热情"},
    "duration": {"total_minutes": 8},
}

# Rules of interest for tracking
CRITICAL_RULES = {"N02", "N05", "N06"}
HIGH_RULES = {"N01", "N03", "N04", "E01", "E02"}
TRACKED_RULES = CRITICAL_RULES | HIGH_RULES


class BenchmarkRun:
    """Captures a single pipeline run with retry tracking."""

    def __init__(self, run_id: int, base_debug_dir: str):
        self.run_id = run_id
        self.run_dir = os.path.join(base_debug_dir, f"p1_run_{run_id:02d}")
        os.makedirs(self.run_dir, exist_ok=True)

        self.initial_warnings = {}   # rule -> count (CW first attempt)
        self.final_warnings = {}     # rule -> count (after any retries)
        self.retry_triggered = False
        self.retry_reason = None     # "error" | "critical_semantic" | "high_semantic" | None
        self.retry_feedback_rules = []  # rules passed as feedback
        self.initial_slides = None   # snapshot of slides after first CW attempt
        self.final_slides = None     # snapshot of slides after retry
        self.errors = 0
        self.pipeline_error = None
        self.duration_sec = 0

    def to_dict(self):
        return {
            "run_id": self.run_id,
            "retry_triggered": self.retry_triggered,
            "retry_reason": self.retry_reason,
            "retry_feedback_rules": self.retry_feedback_rules,
            "initial_warnings": self.initial_warnings,
            "final_warnings": self.final_warnings,
            "warning_delta": {
                rule: self.final_warnings.get(rule, 0) - self.initial_warnings.get(rule, 0)
                for rule in TRACKED_RULES
                if rule in self.initial_warnings or rule in self.final_warnings
            },
            "errors": self.errors,
            "duration_sec": self.duration_sec,
        }


class BenchmarkPipeline(PresentationPipeline):
    """Instrumented pipeline that captures retry details for benchmarking."""

    def __init__(self, *args, bench_run: BenchmarkRun = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.bench = bench_run
        self._attempt = 0
        self._cw_initial_warnings = None

    def _run_agent(self, name: str):
        """Override to capture before/after validator results per attempt."""
        agent = self._create_agent(name)

        feedback = None
        self._attempt = 0

        for attempt in range(agent.max_retries + 1):
            self._attempt = attempt
            if attempt > 0:
                print(f"  [retry {attempt}/{agent.max_retries}]")

            try:
                diff = agent.run(self.state, feedback=feedback)
            except Exception as e:
                # AgentError or API error
                if attempt == agent.max_retries:
                    raise
                continue

            self.state = self._deep_merge_state(self.state, diff)
            result = self.validator.validate_for_agent(self.state, name)
            self._record_validation(name, result)

            if result.errors:
                print(f"  [errors: {len(result.errors)}]")
                for e in result.errors:
                    print(f"    [{e.layer}:{e.rule}] {e.message}")
                if attempt < agent.max_retries:
                    feedback = [
                        {"rule": e.rule, "message": e.message, "severity": "error"}
                        for e in result.errors
                    ]
                    continue
                else:
                    raise Exception(
                        f"Agent {name} has {len(result.errors)} hard errors after {agent.max_retries + 1} attempts"
                    )

            # ---- Capture benchmark data on first CW success ----
            if name == "content_writer" and self.bench:
                rule_counts = self._count_rules(result)
                if attempt == 0 and self._cw_initial_warnings is None:
                    # First attempt — capture initial state
                    self.bench.initial_warnings = rule_counts
                    self.bench.initial_slides = json.loads(json.dumps(
                        self.state.get("slides", []), default=str
                    ))

                # Check if retry should trigger (mirrors pipeline logic)
                critical = {r: c for r, c in rule_counts.items() if r in CRITICAL_RULES}
                high = {r: c for r, c in rule_counts.items() if r in HIGH_RULES}
                total_semantic = sum(rule_counts.values())

                if critical and attempt == 0 and agent.max_retries >= 1:
                    self.bench.retry_triggered = True
                    self.bench.retry_reason = "critical_semantic"
                    self.bench.retry_feedback_rules = list(critical.keys())
                    print(f"  [critical semantic: {sum(critical.values())}] retrying with feedback...")
                    feedback = [
                        {"rule": w.rule, "message": w.message, "severity": w.severity}
                        for w in result.warnings
                        if w.rule in TRACKED_RULES
                    ][:8]
                    continue

                if total_semantic >= 5 and attempt == 0 and agent.max_retries >= 1:
                    self.bench.retry_triggered = True
                    self.bench.retry_reason = "high_semantic"
                    self.bench.retry_feedback_rules = list(high.keys())
                    print(f"  [high semantic load: {total_semantic}] retrying with feedback...")
                    feedback = [
                        {"rule": w.rule, "message": w.message, "severity": w.severity}
                        for w in result.warnings
                        if w.rule in TRACKED_RULES
                    ][:8]
                    continue

                # Final acceptance — capture final state
                self.bench.final_warnings = rule_counts
                self.bench.final_slides = json.loads(json.dumps(
                    self.state.get("slides", []), default=str
                ))
                self.bench.errors = len(result.errors)

            # Accept
            wc = len(result.warnings)
            sc = len(result.suggestions)
            print(f"  [OK] errors=0 warnings={wc} suggestions={sc}")
            if result.warnings:
                for w in result.warnings[:3]:
                    print(f"    [W:{w.rule}] {w.message}")
                if len(result.warnings) > 3:
                    print(f"    ... +{len(result.warnings) - 3} more warnings")
            break

    def _create_agent(self, name):
        from core.agents import create_agent
        agent = create_agent(name, api_key=self.api_key)
        agent.load_prompt(self.prompts_dir)
        if hasattr(agent, "load_base_prompts"):
            agent.load_base_prompts(self.prompts_dir)
        return agent

    def _deep_merge_state(self, base, diff):
        from core.state_manager import deep_merge
        return deep_merge(base, diff)

    @staticmethod
    def _count_rules(result) -> dict:
        """Count warnings by rule id."""
        counts = {}
        for w in result.warnings:
            if w.rule in TRACKED_RULES:
                counts[w.rule] = counts.get(w.rule, 0) + 1
        return counts


def run_benchmark():
    print("=" * 60)
    print("  P1 Convergence Benchmark — 10 runs")
    print(f"  Topic: {TOPIC}")
    print(f"  Style: {STYLE}")
    print(f"  Pages: {PAGES}")
    print(f"  Duration: {CONTEXT['duration']['total_minutes']} min")
    print(f"  Audience: {CONTEXT['audience']['profile']}")
    print("=" * 60)

    # Clean + recreate benchmark dir
    if os.path.exists(BENCH_DIR):
        shutil.rmtree(BENCH_DIR)
    os.makedirs(BENCH_DIR, exist_ok=True)

    schema_path = os.path.join(SCRIPT_DIR, "schemas", "presentation_schema.json")
    prompts_dir = os.path.join(SCRIPT_DIR, "prompts")

    runs = []
    total_success = 0
    total_fail = 0

    for i in range(1, 11):
        print(f"\n{'#' * 60}")
        print(f"  RUN {i:02d}/10")
        print(f"{'#' * 60}")

        br = BenchmarkRun(i, BENCH_DIR)
        t0 = time.time()

        try:
            validator = PresentationValidator(schema_path)
            pipeline = BenchmarkPipeline(
                validator=validator,
                prompts_dir=prompts_dir,
                bench_run=br,
            )

            state = pipeline.run(
                topic=TOPIC,
                style=STYLE,
                pages=PAGES,
                context=CONTEXT,
            )

            # Save final state snapshot
            snap_path = os.path.join(br.run_dir, "final_state.json")
            with open(snap_path, "w", encoding="utf-8") as f:
                json.dump(state, f, ensure_ascii=False, indent=2, default=str)

            # Save initial/final slides diff for before/after analysis
            if br.initial_slides is not None:
                with open(os.path.join(br.run_dir, "slides_before_retry.json"), "w", encoding="utf-8") as f:
                    json.dump(br.initial_slides, f, ensure_ascii=False, indent=2, default=str)
            if br.final_slides is not None:
                with open(os.path.join(br.run_dir, "slides_after_retry.json"), "w", encoding="utf-8") as f:
                    json.dump(br.final_slides, f, ensure_ascii=False, indent=2, default=str)

            total_success += 1
            print(f"\n  RUN {i:02d} OK — retry={br.retry_triggered} "
                  f"init_w={sum(br.initial_warnings.values())} "
                  f"final_w={sum(br.final_warnings.values())}")

        except Exception as e:
            br.pipeline_error = str(e)
            total_fail += 1
            print(f"\n  RUN {i:02d} FAILED: {e}")
            import traceback
            traceback.print_exc()

        br.duration_sec = round(time.time() - t0, 1)
        runs.append(br)

        # Save incremental results
        summary_path = os.path.join(BENCH_DIR, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump({
                "config": {
                    "topic": TOPIC, "style": STYLE, "pages": PAGES,
                    "context": CONTEXT,
                },
                "total_runs": i,
                "success": total_success,
                "fail": total_fail,
                "runs": [r.to_dict() for r in runs],
            }, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"  BENCHMARK COMPLETE")
    print(f"  Success: {total_success}/10  Fail: {total_fail}/10")
    print(f"  Results: {BENCH_DIR}/summary.json")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    run_benchmark()
