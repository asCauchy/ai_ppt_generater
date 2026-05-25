"""Runtime Debug Snapshot — auto-save state after each agent step.

Writes to debug/run_NN/ with timestamped, indented JSON snapshots.
Completely non-invasive: if disabled, zero overhead.
"""

import json
import os
from datetime import datetime


class DebugSnapshot:

    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.run_dir = ""
        self.step = 0

    def start_run(self):
        """Create run_NN directory and return its path."""
        os.makedirs(self.base_dir, exist_ok=True)

        existing = [d for d in os.listdir(self.base_dir)
                    if os.path.isdir(os.path.join(self.base_dir, d)) and d.startswith("run_")]
        next_num = max([int(d.split("_")[1]) for d in existing] + [0]) + 1

        self.run_dir = os.path.join(self.base_dir, f"run_{next_num:02d}")
        os.makedirs(self.run_dir, exist_ok=True)
        self.step = 0
        return self.run_dir

    def snap(self, label: str, state: dict):
        """Save current state as a JSON snapshot."""
        if not self.run_dir:
            return

        self.step += 1
        filename = f"{self.step:02d}_{label}.json"
        path = os.path.join(self.run_dir, filename)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def snap_initial(self, state: dict):
        self.snap("state_initial", state)

    def snap_after_agent(self, agent_name: str, state: dict):
        self.snap(f"state_after_{agent_name}", state)

    def snap_final(self, state: dict):
        self.snap("state_final", state)

    def write_summary(self, pipeline_log: list[dict]):
        """Write a human-readable run summary alongside snapshots."""
        if not self.run_dir:
            return
        path = os.path.join(self.run_dir, "run_summary.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "run_dir": self.run_dir,
                "timestamp": datetime.now().isoformat(),
                "steps": pipeline_log,
            }, f, ensure_ascii=False, indent=2)
