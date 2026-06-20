# Day 4 Implementation Log

## Scope

Integrate the Day 3 min-cost max-flow algorithm into the scheduler layer so the
CLI can run:

```bash
python main.py --scheduler flow --seed 42
```

## Log

1. Read the Day 4 roadmap section and current scheduler code.
   - Why: Day 4 is specifically scheduler integration, not a new simulator
     lifecycle.
   - Why this beats alternatives: adding a new scheduler class keeps the OOP
     boundary clean; branching inside `Simulator` would couple the simulator to
     one algorithm.

2. Added `FlowScheduler` as a `Scheduler` subclass.
   - Why: all existing scheduling strategies expose the same `schedule()` API.
   - Why this beats alternatives: the simulator can keep calling
     `self.scheduler.schedule(...)` polymorphically.

3. Built a graph per scheduling tick using `source -> jobs -> servers -> sink`.
   - Why: the available jobs and server capacity change over time.
   - Why this beats alternatives: a stale global graph would not reflect current
     GPU availability after completed or failed jobs release resources.

4. Used the existing Dijkstra + Johnson-potential `MinCostFlow` implementation.
   - Why: this keeps Day 3's optimized algorithm as the core.
   - Why this beats alternatives: SPFA/Bellman-Ford would be slower and was
     explicitly rejected for this project.

5. Added a non-negative cost function using server cost, latency, deadline risk,
   failure risk, region mismatch, and priority.
   - Why: Dijkstra with zero initial potentials needs non-negative public edge
     costs.
   - Why this beats alternatives: subtracting a large priority bonus can create
     negative costs and force Bellman-Ford initialization.

6. Added a final GPU-capacity guard while extracting assignments.
   - Why: one flow unit represents one job, but jobs can request more than one
     GPU.
   - Why this beats alternatives: exact all-or-nothing multi-GPU modeling would
     require a more complex formulation; this keeps Day 4 correct and simple.

7. Added `flow` to the scheduler factory and CLI choices.
   - Why: `main.py --scheduler flow` is the Day 4 deliverable.
   - Why this beats alternatives: the existing factory is the central scheduler
     construction point.

8. Added focused flow-scheduler tests.
   - Why: Day 3 tested the algorithm; Day 4 needs tests for graph integration
     and scheduler behavior.
   - Why this beats alternatives: only testing the CLI would miss assignment
     extraction and capacity bugs.

9. Ran focused and full tests.
   - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_flow_scheduler.py`
   - Result: `5 passed`
   - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
   - Result: `19 passed`
   - Why: focused tests prove the new scheduler behavior; the full suite checks
     that Day 4 did not break Day 2 or Day 3.
   - Why this beats alternatives: a single CLI smoke test can pass while edge
     cases like GPU over-allocation remain broken.

10. Ran same-seed scheduler comparison with `--seed 42`.
    - FCFS: `35/39` completed, `0` misses, `25.7%` utilization, `586.88` cost.
    - EDF: `35/39` completed, `0` misses, `25.7%` utilization, `586.88` cost.
    - Priority: `35/39` completed, `0` misses, `25.7%` utilization, `586.88` cost.
    - Flow: `35/39` completed, `0` misses, `26.2%` utilization, `612.66` cost.
    - Why: the roadmap asks for a comparison against greedy schedulers.
    - Why this beats alternatives: using real local outputs avoids documenting
      invented or aspirational results.

11. Ran a larger flow smoke test.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 main.py --scheduler flow --jobs 100 --servers 12 --agents 20 --data-centers 3 --seed 42`
    - Result: `88/100` completed, `0` misses, `28.3%` utilization, `2077.93` cost.
    - Why: the README shows this style of workload-size override.
    - Why this beats alternatives: testing only the default workload could miss
      graph-size or CLI-argument integration issues.
