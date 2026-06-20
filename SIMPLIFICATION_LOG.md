# Simplification Log

## Goal

Make CloudArena easier to explain in an interview by removing fields that were
mostly useful for auction/game-theory or stochastic-runtime extensions.

## Removed Concepts

1. Private value.
   - Why removed: it belonged to the skipped auction/game-theory path.
   - Result: the flow scheduler no longer needs a user valuation to score
     failure risk.

2. Budget.
   - Why removed: the project no longer accepts bids or payments.
   - Result: a job is now only a workload request, not an economic bid.

3. Mean duration and standard deviation.
   - Why removed: two duration fields made the dry run harder to explain.
   - Result: every job has one `duration`.

4. Runtime uncertainty toggle.
   - Why removed: runtime uncertainty depended on the removed standard
     deviation field.
   - Result: duration is deterministic; probability remains through server
     failure trials and generated arrival variation.

## Current Job Shape

```txt
job_id
user_id
arrival_time
deadline
duration
gpu_required
priority
region
```

## Dry Run Template

The dynamic dashboard now has a `Dry Run` button. It preloads:

- 2 regions: `us-east`, `europe`
- 2 data centers
- 2 servers
- 3 jobs

This gives a small example where the interviewer can see waiting jobs, running
jobs, server assignment, GPU usage, and timeline changes after stepping the
clock.

## Verification

- Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile app.py main.py cloudarena/*.py`
- Result: passed
- Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
- Result: `34 passed`
- Command: `PYTHONDONTWRITEBYTECODE=1 python3 main.py --scheduler flow --jobs 5 --servers 2 --agents 2 --data-centers 1 --seed 42`
- Result: completed without errors
