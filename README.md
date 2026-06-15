
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
```
