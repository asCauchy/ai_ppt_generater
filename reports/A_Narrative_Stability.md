# Narrative Stability Analysis

## A1. Narrative Role Sequence Stability

- Run 1: 100% match with Run 1 (7/7 roles identical)
- Run 2: 57% match with Run 1 (4/7 roles identical)
  Differences: [(3, 'evidence', 'insight'), (4, 'insight', 'conflict'), (5, 'recap', 'vision')]
- Run 3: 86% match with Run 1 (6/7 roles identical)
- Run 4: 86% match with Run 1 (6/7 roles identical)
- Run 5: 57% match with Run 1 (4/7 roles identical)
  Differences: [(3, 'evidence', 'insight'), (4, 'insight', 'conflict'), (5, 'recap', 'vision')]

## A2. Section Topology

- Structure distribution: {'起承转合': 5}
- Section count distribution: {4: 5}

- Stable roles (present in ALL runs): ['call_to_action', 'context', 'evidence', 'hook', 'insight']
- Drift roles (not universally present): ['conflict', 'recap', 'vision']

## A3. CTA & Hook Placement

- Run 1: hook at [0], CTA at [6]
- Run 2: hook at [0], CTA at [6]
- Run 3: hook at [0], CTA at [6]
- Run 4: hook at [0], CTA at [6]
- Run 5: hook at [0], CTA at [6]

## A4. Topology Variance Score: 29%

(0% = identical across all runs, 100% = completely different each run)
Interpretation: STABLE