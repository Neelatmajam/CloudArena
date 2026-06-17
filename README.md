
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

## How to Run

```bash
python main.py --scheduler fcfs --seed 1
python main.py --scheduler edf --seed 1
python main.py --scheduler priority --seed 1
```

You can also change workload size:

```bash
python main.py --scheduler priority --jobs 100 --servers 12 --agents 20 --seed 42
```

## Tests

```bash
pytest
pytest tests/test_flow.py
```
