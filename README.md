
# CloudArena

CloudArena is a GPU cloud workload scheduling simulator. It compares scheduling
strategies for assigning AI/ML jobs to a limited set of GPU servers.

## Problem Statement

Users submit GPU jobs with arrival times, deadlines, priorities, budgets, and
resource requirements. CloudArena simulates a data center deciding which jobs
should run on which servers while tracking completion rate, deadline misses,
wait time, GPU utilization, and cost.

The simulator records five job-status timelines at each time step: `waiting`,
`running`, `completed`, `failed`, and `rejected`.

## System Design

The project currently has these core objects:

- `Job`: a GPU workload submitted by a user.
- `Agent`: a user/customer who owns jobs.
- `Server`: a machine with limited GPU capacity.
- `DataCenter`: a group of servers in one region.
- `SimulationConfig`: the settings for one simulator run.

## Baseline Schedulers

### FCFS

First-come, first-served schedules jobs by arrival time, using `job_id` as the
tie-breaker.

### Earliest Deadline First

EDF schedules jobs with the closest deadline first. Priority and expected
duration are used as tie-breakers.

### Priority Scheduler

The priority scheduler schedules higher-priority jobs first, then uses deadline
and expected duration as tie-breakers.

## Core Algorithm: Min-Cost Max-Flow

Day 3 adds a standalone min-cost max-flow implementation in
`cloudarena/min_cost_flow.py`. It models scheduling as a directed residual graph:

```txt
source -> jobs -> servers -> sink
```

Each edge has capacity and cost. Sending one unit of flow through a job-server
edge means assigning that job to that server. Reverse edges are added
automatically so later augmenting paths can undo an earlier choice when that
leads to a lower global cost.

The current implementation uses the successive shortest augmenting path method
with Dijkstra and Johnson-style potentials over residual edges. Public edge
costs are kept non-negative; reverse edges may have negative original costs, but
potentials reweight residual edges so Dijkstra can still be used correctly after
each augmentation. For `F` units of flow, `V` nodes, and `E` edges, the rough
time complexity is `O(F * E log V)`.

## Flow Scheduler

The flow scheduler integrates the min-cost max-flow algorithm with the simulator.
At every scheduling tick it builds a fresh graph:

```txt
source -> waiting jobs -> available servers -> sink
```

Each selected job-server edge becomes one proposed assignment. The simulator
still performs the final validation before starting jobs, so all schedulers keep
the same `[(job_id, server_id), ...]` contract.

## Cost Function

The flow scheduler uses a non-negative cost function so Dijkstra with potentials
can run without Bellman-Ford initialization:

```txt
server cost      = server.cost_per_tick * job.duration_mean
latency cost     = server.latency
deadline penalty = lateness * 20
failure penalty  = server.failure_probability * job.private_value
region penalty   = 25 if job and server regions differ
priority cost    = 10 - job.priority
```

This makes cheaper, lower-latency, lower-risk, same-region, higher-priority
placements more attractive to the optimizer.

## Greedy vs Flow Results

These results use the default workload size and `--seed 42`.

| Scheduler | Completed | Failed | Rejected | Deadline Misses | Avg Wait | GPU Utilization | Total Cost |
|---|---:|---:|---:|---:|---:|---:|---:|
| FCFS | 36/39 | 3 | 0 | 0 | 0.00 | 18.1% | 788.52 |
| EDF | 38/39 | 1 | 0 | 0 | 0.00 | 18.2% | 780.90 |
| Priority | 38/39 | 1 | 0 | 0 | 0.00 | 16.7% | 733.60 |
| Flow | 37/39 | 2 | 0 | 0 | 0.13 | 18.4% | 723.60 |

Flow is now integrated and globally optimizes the modeled placement cost. The
first cost function is intentionally simple; later tuning can make the modeled
objective line up more strongly with completion rate, deadline misses, and total
simulator cost.

## Stochastic Simulation

CloudArena now has an explicit probability layer in `cloudarena/probability.py`.
The simulator uses three stochastic pieces:

- Runtime uncertainty: each started job samples `actual_duration` around
  `duration_mean` and `duration_std`.
- Server failures: each running job performs a Bernoulli failure trial each
  tick using `server.failure_probability`.
- Arrival variation: generated jobs mix early arrivals, peak-hour arrivals, and
  late arrivals inside the configured time horizon.

The auction/game-theory scheduler is intentionally skipped to keep this version
focused on scheduling, probability, and Monte Carlo evaluation.

## Monte Carlo Evaluation

Use repeated runs when you want statistically meaningful results:

```bash
python main.py --scheduler flow --runs 30 --seed 42
python main.py --compare-all --runs 30 --seed 42
```

Monte Carlo results are exported to:

```txt
results/monte_carlo_results.csv
```

The table below uses `python main.py --compare-all --runs 30 --seed 42`.

| Scheduler | Avg Completed | Avg Misses | Avg Wait | Avg Utilization | Avg Cost | Std Completed | Std Misses | Std Utilization |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| FCFS | 35.13 | 0.20 | 0.45 | 28.0% | 855.76 | 2.08 | 0.65 | 12.48 |
| EDF | 34.93 | 0.07 | 0.36 | 27.7% | 842.89 | 2.08 | 0.25 | 12.76 |
| Priority | 35.00 | 0.27 | 0.32 | 27.2% | 829.55 | 2.10 | 0.73 | 12.23 |
| Flow | 34.87 | 0.17 | 0.31 | 27.2% | 792.75 | 2.38 | 0.45 | 11.95 |

## How to Run

```bash
python main.py --scheduler fcfs --seed 1
python main.py --scheduler edf --seed 1
python main.py --scheduler priority --seed 1
python main.py --scheduler flow --seed 42
python main.py --scheduler flow --runs 30 --seed 42
python main.py --compare-all --runs 30 --seed 42
```

You can also change workload size:

```bash
python main.py --scheduler flow --jobs 100 --servers 12 --agents 20 --seed 42
```

## Tests

```bash
pytest
pytest tests/test_flow.py
```
