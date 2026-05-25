"""Presentation Pipeline — state-based multi-agent orchestration.

The pipeline is NOT a linear script. It is a state evolution runtime:
  - each agent receives the full state
  - each agent returns a state diff
  - diff is merged into the master state
  - validator runs on the agent's output layer
  - on error → retry; on warning → annotate history
"""

from __future__ import annotations

import os

from .state_manager import deep_merge, init_presentation_state
from .agents import create_agent, AgentError
from .validator import PresentationValidator
from .debug_snapshot import DebugSnapshot


class PipelineError(Exception):
    pass


class PresentationPipeline:

    def __init__(
        self,
        validator: PresentationValidator,
        prompts_dir: str,
        api_key: str = None,
        debug: bool = False,
    ):
        self.validator = validator
        self.prompts_dir = prompts_dir
        self.api_key = api_key
        self.debug = debug
        self.snapshot = DebugSnapshot(os.path.join(os.path.dirname(prompts_dir), "debug")) if debug else None
        self.state: dict = {}
        self._step_log: list[dict] = []

    # ---- public API ----

    def run(self, topic: str, style: str, pages: int, context: dict = None) -> dict:
        """Execute the full pipeline against a new presentation.

        Returns the final Presentation State.
        """
        self.state = init_presentation_state(topic, style, pages, context)
        self._step_log = []

        if self.snapshot:
            self.snapshot.start_run()
            self.snapshot.snap_initial(self.state)
            print(f"\n[debug] snapshot → {self.snapshot.run_dir}")

        # ---- Agent 1: Narrative Planner ----
        self._run_agent("narrative_planner")

        # ---- Agent 2: Content Writer ----
        self._run_agent("content_writer")

        if self.snapshot:
            self.snapshot.snap_final(self.state)
            self.snapshot.write_summary(self._step_log)

        return self.state

    def run_partial(self, state: dict, agent_names: list[str]) -> dict:
        """Run a subset of agents on an existing state. For incremental updates."""
        self.state = state
        self._step_log = []
        for name in agent_names:
            self._run_agent(name)
        return self.state

    # ---- internal ----

    def _run_agent(self, name: str):
        print(f"\n{'=' * 50}")
        print(f"  Agent: {name}")
        print(f"{'=' * 50}")

        agent = create_agent(name, api_key=self.api_key)
        agent.load_prompt(self.prompts_dir)

        # Optional: load shared prompts for NarrativePlanner
        if hasattr(agent, "load_base_prompts"):
            agent.load_base_prompts(self.prompts_dir)

        feedback = None  # accumulates across retries

        for attempt in range(agent.max_retries + 1):
            if attempt > 0:
                print(f"  [retry {attempt}/{agent.max_retries}]")

            try:
                diff = agent.run(self.state, feedback=feedback)
            except AgentError as e:
                print(f"  [AgentError] {e}")
                if attempt == agent.max_retries:
                    raise PipelineError(f"Agent {name} failed after {agent.max_retries + 1} attempts: {e}")
                continue

            # Merge diff into master state
            self.state = deep_merge(self.state, diff)

            # Validate
            result = self.validator.validate_for_agent(self.state, name)

            # Attach validation result to history
            self._record_validation(name, result)

            if result.errors:
                print(f"  [errors: {len(result.errors)}]")
                for e in result.errors:
                    print(f"    [{e.layer}:{e.rule}] {e.message}")
                if attempt < agent.max_retries:
                    # Build error feedback and retry
                    feedback = [
                        {"rule": e.rule, "message": e.message, "severity": "error"}
                        for e in result.errors
                    ]
                    continue
                else:
                    raise PipelineError(
                        f"Agent {name} has {len(result.errors)} hard errors after {agent.max_retries + 1} attempts"
                    )

            # No hard errors. Check for critical semantic warnings worth a retry.
            critical_warnings = [
                w for w in result.warnings
                if w.rule in ("N02", "N05", "N06")  # conflict collapse, vision drift, weak CTA
            ]
            high_warnings = [
                w for w in result.warnings
                if w.rule.startswith(("N0", "E0")) and w.rule not in ("N02", "N05", "N06")
            ]

            total_semantic = len(critical_warnings) + len(high_warnings)

            if critical_warnings and attempt == 0 and agent.max_retries >= 1:
                print(f"  [critical semantic: {len(critical_warnings)}] retrying with feedback...")
                for w in critical_warnings:
                    print(f"    [{w.rule}] {w.message[:100]}")
                feedback = [
                    {"rule": w.rule, "message": w.message, "severity": w.severity}
                    for w in (critical_warnings + high_warnings)[:8]
                ]
                continue

            if total_semantic >= 5 and attempt == 0 and agent.max_retries >= 1:
                print(f"  [high semantic load: {total_semantic}] retrying with feedback...")
                feedback = [
                    {"rule": w.rule, "message": w.message, "severity": w.severity}
                    for w in (critical_warnings + high_warnings)[:8]
                ]
                continue

            # Accept
            print(f"  [OK] errors=0 warnings={len(result.warnings)} suggestions={len(result.suggestions)}")
            if result.warnings:
                for w in result.warnings[:3]:
                    print(f"    [W:{w.rule}] {w.message}")
                if len(result.warnings) > 3:
                    print(f"    ... +{len(result.warnings) - 3} more warnings")

            if self.snapshot:
                self.snapshot.snap_after_agent(name, self.state)

            break

    def _record_validation(self, agent_name: str, result):
        entry = {
            "agent": agent_name,
            "errors": len(result.errors),
            "warnings": len(result.warnings),
            "suggestions": len(result.suggestions),
            "error_details": [{"rule": e.rule, "message": e.message} for e in result.errors],
            "warning_details": [{"rule": w.rule, "message": w.message} for w in result.warnings],
        }
        self._step_log.append(entry)

        # Also update state's runtime.history last entry
        runtime = self.state.get("runtime", {})
        history = runtime.get("history", [])
        if history:
            history[-1]["validation"] = {
                "errors": len(result.errors),
                "warnings": len(result.warnings),
                "suggestions": len(result.suggestions),
            }
            runtime["history"] = history
            self.state["runtime"] = runtime

    @property
    def step_log(self):
        return list(self._step_log)
