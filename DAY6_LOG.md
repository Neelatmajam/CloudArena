# Day 6 Implementation Log

## Scope

Implement probability and Monte Carlo simulation while explicitly skipping the
auction/game-theory track.

The implemented schedulers for Day 6 are:

```txt
fcfs
edf
priority
flow
```

## Log

1. Read the Day 6 roadmap and current simulator.
   - Why: Day 6 is about stochastic runtime, failures, random arrivals, repeated
     simulation, summary statistics, and CSV export.
   - Why this beats alternatives: implementing the auction path now would expand
     the project into game theory, which the project owner explicitly chose to
     skip.

2. Created `cloudarena/probability.py`.
   - Why: runtime sampling, failure trials, and arrival sampling are probability
     concerns, not scheduler concerns.
   - Why this beats alternatives: keeping random-variable helpers in one module
     makes them testable and prevents probability logic from being scattered
     across workload generation and simulation.

3. Added stochastic runtime sampling.
   - Why: Day 2 used `duration_mean` exactly, so repeated runs differed mostly
     by workload seed and failure events.
   - Result: each started job now samples `actual_duration` from a bounded
     Gaussian-style rule: `max(1, round(gauss(mean, std)))`.

4. Kept server failures as Bernoulli trials but routed them through
   `should_fail()`.
   - Why: the simulator already had failure probability, but the logic was inline.
   - Result: the probability model is now explicit and unit-testable.

5. Improved random job arrivals.
   - Why: uniform early arrivals are simple but hide burst/late-arrival behavior.
   - Result: arrivals now mix early, peak-hour, and late arrivals while staying
     inside the configured time horizon.

6. Created `cloudarena/monte_carlo.py`.
   - Why: Monte Carlo is an experiment runner, separate from one simulation.
   - Why this beats alternatives: putting this in `main.py` would make the CLI
     hard to test and would mix experiment orchestration with argument parsing.

7. Added `--runs`, `--compare-all`, `--export`, `--failure-probability`, and
   `--deterministic-runtime` CLI flags.
   - Why: Day 6 needs repeated simulations and reproducible experiment exports.
   - Result: single-run behavior still works, and `--runs` activates Monte Carlo.

8. Skipped auction/game-theory metrics intentionally.
   - Why: the project owner decided the game-theory part would make the project
     too complicated.
   - Result: CSV exports focus on simulation metrics: completion, failures,
     rejections, deadline misses, wait time, completion time, utilization, and
     cost.

9. Added tests for probability and Monte Carlo behavior.
   - Why: Day 6 changes affect randomness, so deterministic tests need fixed
     seeds and boundary cases.
   - Result: tests cover runtime bounds, failure probability boundaries, arrival
     bounds, Monte Carlo seed progression, summary statistics, and CSV export.

10. Ran focused and full verification.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_probability.py tests/test_monte_carlo.py`
    - Result: `7 passed`
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
    - Result: `26 passed`
    - Why this beats alternatives: testing only the CLI would not prove the
      random-variable helpers or summary/export logic are individually correct.

11. Ran a 5-run Monte Carlo smoke test.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 main.py --scheduler flow --runs 5 --jobs 20 --servers 4 --agents 5 --data-centers 2 --seed 42 --export /tmp/cloudarena_mc_smoke.csv`
    - Result: `17.80` average completed jobs, `0.00` average deadline misses,
      `9.6%` average utilization, `298.91` average cost.
    - Why: fast smoke run proves the CLI, repeated simulation, summary output,
      and CSV writer work together.

12. Ran the Day 6 30-run comparison without auction.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 main.py --compare-all --runs 30 --seed 42 --export results/monte_carlo_results.csv`
    - FCFS: `35.13` avg completed, `0.20` avg misses, `28.0%` avg utilization,
      `855.76` avg cost.
    - EDF: `34.93` avg completed, `0.07` avg misses, `27.7%` avg utilization,
      `842.89` avg cost.
    - Priority: `35.00` avg completed, `0.27` avg misses, `27.2%` avg
      utilization, `829.55` avg cost.
    - Flow: `34.87` avg completed, `0.17` avg misses, `27.2%` avg utilization,
      `792.75` avg cost.
    - Result: wrote `results/monte_carlo_results.csv` with `120` run rows plus
      a header.
    - Why this beats alternatives: a single run can be noisy or misleading;
      repeated runs show averages and variability.

13. Refreshed the single-run README comparison after adding stochastic runtime
    and arrival sampling.
    - Why: the Day 4 table changed once Day 6 probability entered the simulator.
    - Result: README now reports the current `--seed 42` single-run values for
      FCFS, EDF, Priority, and Flow.
