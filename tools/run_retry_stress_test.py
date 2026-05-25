"""Targeted retry stress test — inject known-complex state, test CW retry.

Uses the original debug run states (7 slides, rich narrative roles) to test
whether the semantic feedback loop can actually fix N02/N05/N06 issues.
"""

import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.pipeline import PresentationPipeline
from core.validator import PresentationValidator
from core.agents.content_writer import ContentWriter
from core.state_manager import deep_merge

SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(SCRIPT_DIR, "debug", "p1_retry_stress_test")
os.makedirs(RESULTS_DIR, exist_ok=True)


def run_retry_test(state: dict, label: str, validator: PresentationValidator):
    """Run ContentWriter with retry loop on a given state. Returns detailed results."""
    cw = ContentWriter()
    cw.load_prompt(os.path.join(SCRIPT_DIR, "prompts"))

    results = {
        "label": label,
        "attempts": [],
    }

    feedback = None
    for attempt in range(cw.max_retries + 1):
        attempt_data = {
            "attempt": attempt,
            "has_feedback": feedback is not None,
            "feedback_rules": [f["rule"] for f in feedback] if feedback else [],
        }

        try:
            diff = cw.run(state, feedback=feedback)
        except Exception as e:
            attempt_data["error"] = str(e)
            results["attempts"].append(attempt_data)
            break

        merged = deep_merge(state, diff)
        result = validator.validate(merged)

        # Count semantic warnings
        semantic_warnings = [w for w in result.warnings if w.rule.startswith(("N0", "E0"))]
        critical = [w for w in semantic_warnings if w.rule in ("N02", "N05", "N06")]

        attempt_data["state_snapshot"] = {
            "total_warnings": len(result.warnings),
            "semantic_warnings": len(semantic_warnings),
            "critical_warnings": len(critical),
            "warning_rules": list(set(w.rule for w in semantic_warnings)),
            "critical_rules": list(set(w.rule for w in critical)),
            "warning_details": [
                {"rule": w.rule, "message": w.message[:120]}
                for w in semantic_warnings
            ],
        }
        attempt_data["errors"] = len(result.errors)

        # Save merged state snapshot
        snap_path = os.path.join(RESULTS_DIR, f"{label}_attempt{attempt}.json")
        with open(snap_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2, default=str)

        results["attempts"].append(attempt_data)
        state = merged  # update for next iteration

        # Determine if we should retry
        if result.errors:
            if attempt < cw.max_retries:
                feedback = [{"rule": e.rule, "message": e.message, "severity": "error"} for e in result.errors]
                continue
            else:
                break

        if critical and attempt == 0 and cw.max_retries >= 1:
            print(f"    -> Retry triggered: {[w.rule for w in critical]}")
            feedback = [{"rule": w.rule, "message": w.message, "severity": "warning"} for w in semantic_warnings[:8]]
            continue

        if len(semantic_warnings) >= 5 and attempt == 0 and cw.max_retries >= 1:
            print(f"    -> Retry triggered: {len(semantic_warnings)} semantic warnings")
            feedback = [{"rule": w.rule, "message": w.message, "severity": "warning"} for w in semantic_warnings[:8]]
            continue

        break  # accept

    return results


def main():
    validator = PresentationValidator(os.path.join(SCRIPT_DIR, "schemas", "presentation_schema.json"))

    # Load states from the original debug runs (narrative-planned, before CW)
    test_states = []
    for run_name in ["run_02", "run_05"]:
        path = os.path.join(SCRIPT_DIR, "debug", run_name, "02_state_after_narrative_planner.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                state = json.load(f)
            # Strip any existing content_writer output to start fresh
            for s in state.get("slides", []):
                content = s.get("content", {})
                for key in ["points", "data", "visual_description"]:
                    content.pop(key, None)
                s.pop("emotional_role", None)
                s.pop("presentation_role", None)
                s.pop("notes", None)
            test_states.append((run_name, state))

    print(f"Loaded {len(test_states)} test states with complex narrative structures\n")

    all_results = {}
    for label, state in test_states:
        print(f"{'='*60}")
        print(f"  Retry Test: {label}")
        slides_n = len(state.get("slides", []))
        roles = [s.get("narrative_role") for s in state.get("slides", [])]
        print(f"  Slides: {slides_n}")
        print(f"  Roles: {roles}")
        print(f"{'='*60}")

        result = run_retry_test(state, label, validator)
        all_results[label] = result

        for a in result["attempts"]:
            snap = a.get("state_snapshot", {})
            fb = "with feedback" if a["has_feedback"] else "no feedback"
            print(f"  Attempt {a['attempt']} ({fb}): "
                  f"errors={a.get('errors', '?')} "
                  f"warnings={snap.get('total_warnings', '?')} "
                  f"semantic={snap.get('semantic_warnings', '?')} "
                  f"critical={snap.get('critical_warnings', '?')}")
            if snap.get("warning_details"):
                for wd in snap["warning_details"][:3]:
                    print(f"    [{wd['rule']}] {wd['message'][:100]}")

        # Calculate delta
        if len(result["attempts"]) >= 2:
            a0 = result["attempts"][0].get("state_snapshot", {})
            a1 = result["attempts"][-1].get("state_snapshot", {})
            delta = a1.get("semantic_warnings", 0) - a0.get("semantic_warnings", 0)
            print(f"  Delta: {a0.get('semantic_warnings', 0)} -> {a1.get('semantic_warnings', 0)} ({delta:+d})")
        print()

    # Save results
    results_path = os.path.join(RESULTS_DIR, "retry_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2, default=str)

    print(f"Results saved to {results_path}")


if __name__ == "__main__":
    main()
