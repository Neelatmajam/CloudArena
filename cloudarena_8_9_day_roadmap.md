# CloudArena: 8-9 Day Internship-Ready Project Roadmap

## Project Overview

**Project name:** CloudArena  
**Full title:** CloudArena: A Game-Theoretic GPU Cloud Scheduler using Min-Cost Flow, Monte Carlo Simulation, and Auction Mechanisms

CloudArena is a realistic simulator where users submit AI/ML jobs to a limited cloud GPU cluster. Your system decides which jobs should run on which servers using different scheduling strategies.

You will compare:

| Scheduler | Main concept |
|---|---|
| FCFS Scheduler | First-come, first-served baseline |
| Earliest Deadline First Scheduler | Greedy scheduling by closest deadline |
| Priority Scheduler | Greedy scheduling by priority and deadline |
| Min-Cost Flow Scheduler | Graph optimization for job-server assignment |
| Auction Scheduler | Game-theoretic GPU allocation using bids |

The project combines:

| Area | What you will build |
|---|---|
| Data Structures and Algorithms | Priority queues, graphs, residual networks, min-cost max-flow, greedy scheduling |
| OOP | `Job`, `Server`, `DataCenter`, `Agent`, `Scheduler`, `Simulator`, `Metrics` classes |
| Probability | Random job arrivals, uncertain runtime, server failures, Monte Carlo simulation |
| Game Theory | Second-price auctions, strategic agents, utility, revenue, social welfare |
| Python/C++ | Python for the complete project; optional C++ implementation of min-cost flow |

---

## Why This Project Is Strong for Internships

This is not a basic CRUD app. It looks like a small version of systems that large tech companies actually care about: cloud scheduling, AI infrastructure, distributed resource allocation, cost optimization, and system reliability.

Real-world inspiration:

- Google Research has worked on cloud VM scheduling and resource efficiency through systems like LAVA.
- Microsoft Research has worked on Singularity, a globally distributed scheduling service for deep learning training and inference workloads.
- Kubernetes uses a scheduling framework where scheduling logic can be modular and extensible.
- Cloud providers increasingly care about GPU allocation, AI workloads, cost, failures, latency, and utilization.

Your project will show that you can combine algorithmic thinking with practical system design.

---

## Final GitHub Description

> A GPU cloud workload scheduling simulator that compares greedy, min-cost flow, and auction-based allocation under stochastic runtime uncertainty and server failures.

---

## Recommended Language

Use **Python** for the main project.

Reason:

- Faster to finish in 8-9 days.
- Easier to build simulations, tests, CSV exports, and Streamlit dashboard.
- Easier to demonstrate probability and Monte Carlo experiments.
- You can still implement the core algorithm, min-cost flow, from scratch.

Optional:

- Add a standalone C++ version of min-cost flow on Day 9 if the Python project is already complete.

Recommended stack:

```txt
Python 3.11+
pytest
matplotlib
streamlit
```

Avoid using heavy algorithm libraries like NetworkX for the core algorithms. Implement min-cost flow yourself so the project clearly demonstrates DSA skill.

---

## Final Project Scope

By the end, your repository should contain:

```txt
cloudarena/
│
├── cloudarena/
│   ├── __init__.py
│   ├── models.py
│   ├── workload.py
│   ├── simulator.py
│   ├── schedulers.py
│   ├── min_cost_flow.py
│   ├── auction.py
│   ├── probability.py
│   ├── metrics.py
│   └── config.py
│
├── tests/
│   ├── test_greedy.py
│   ├── test_flow.py
│   ├── test_auction.py
│   └── test_metrics.py
│
├── results/
│   ├── sample_results.csv
│   └── monte_carlo_results.csv
│
├── screenshots/
│   └── dashboard.png
│
├── app.py
├── main.py
├── requirements.txt
└── README.md
```

Optional C++ structure:

```txt
cpp/
└── min_cost_flow.cpp
```

---

## Daily Rule

Every day should end with:

```txt
1 working feature
1 small test
1 Git commit
1 README update
```

Do not wait until the end to write the README. Recruiters often read the README before reading code.

Recommended daily time split:

```txt
1 hour learning
5-6 hours coding
1 hour testing/debugging
30 minutes README/GitHub polish
```

---

## MVP Definition

Your minimum viable project should include:

```txt
OOP models
Workload generator
Simulator engine
FCFS scheduler
EDF scheduler
Priority scheduler
Min-cost flow scheduler
Auction scheduler
Probability module
Monte Carlo runner
CSV result export
Streamlit dashboard
README with results and screenshots
```

Optional after MVP:

```txt
C++ min-cost flow implementation
More detailed charts
More agent strategies
More advanced cost function
Dijkstra with potentials for min-cost flow
```

---

# Day 1 — Project Design, OOP Models, and Workload Generator

## Goal

Create the project structure and define the main objects of the system.

By the end of Day 1, you should be able to generate a fake cloud workload containing jobs, users, servers, and data centers.

---

## What You Will Learn

You will learn practical OOP design:

```txt
class design
composition
inheritance
interfaces
data modeling
object relationships
```

You will also understand how real schedulers think:

```txt
jobs arrive
servers have limited capacity
scheduler chooses placement
metrics measure quality
```

---

## Resources to Refer

Read only the needed parts. Do not try to finish every resource fully.

1. Google Research LAVA blog  
   https://research.google/blog/solving-virtual-machine-puzzles-how-ai-is-optimizing-cloud-computing/

2. Microsoft Research AI Infrastructure / Singularity  
   https://www.microsoft.com/en-us/research/project/ai-infrastructure/

3. Python dataclasses documentation  
   https://docs.python.org/3/library/dataclasses.html

4. Kubernetes Scheduling Framework  
   https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/

---

## Files to Create

```txt
cloudarena/__init__.py
cloudarena/models.py
cloudarena/workload.py
cloudarena/config.py
main.py
requirements.txt
README.md
```

---

## Classes to Design

In `models.py`, create these classes:

```txt
Job
Server
DataCenter
Agent
SimulationConfig
```

Use Python `@dataclass` for these classes.

---

## Job Fields

```txt
job_id
user_id
arrival_time
deadline
duration_mean
duration_std
gpu_required
budget
private_value
priority
region
status
start_time
finish_time
assigned_server
actual_duration
payment
utility
```

Possible job statuses:

```txt
WAITING
RUNNING
COMPLETED
FAILED
REJECTED
```

---

## Server Fields

```txt
server_id
data_center_id
region
gpu_capacity
available_gpus
cost_per_tick
failure_probability
latency
running_jobs
```

---

## Agent Fields

```txt
agent_id
strategy
budget
private_value_multiplier
```

Possible strategies:

```txt
truthful
underbid
overbid
random
deadline_panic
```

---

## DataCenter Fields

```txt
data_center_id
region
servers
energy_cost
base_latency
```

---

## SimulationConfig Fields

```txt
num_jobs
num_servers
num_agents
num_data_centers
time_horizon
seed
default_failure_probability
runtime_uncertainty
```

---

## Workload Generator

Create a function:

```txt
generate_workload(config, seed)
```

It should generate:

```txt
N jobs
M servers
K agents/users
D data centers
```

Use fixed random seeds so your experiments are reproducible.

Example generated job:

```txt
Job 12:
arrival_time = 5
deadline = 22
duration_mean = 6
gpu_required = 1
budget = 80
private_value = 120
priority = 3
region = "asia"
```

Example generated server:

```txt
Server 3:
region = "us-east"
gpu_capacity = 4
available_gpus = 4
cost_per_tick = 3
failure_probability = 0.02
latency = 10
```

---

## Day 1 Implementation Steps

1. Create GitHub repository.
2. Create project folders.
3. Add `requirements.txt`.
4. Add `Job`, `Server`, `DataCenter`, `Agent`, and `SimulationConfig` classes.
5. Add workload generator.
6. Add command-line seed support in `main.py`.
7. Print generated workload summary.
8. Commit code.
9. Update README.

---

## Day 1 Deliverable

You should be able to run:

```bash
python main.py --seed 42
```

Expected output:

```txt
Generated 100 jobs
Generated 12 servers
Generated 20 users
Generated 3 data centers
```

---

## Day 1 README Update

Add these sections:

```txt
# CloudArena
## Problem Statement
## Why this project matters
## Real-world inspiration
## System design
```

Mention that your project is inspired by cloud scheduling, AI workload placement, and resource optimization.

---

## Day 1 Acceptance Checklist

```txt
[ ] GitHub repo created
[ ] Project folders created
[ ] requirements.txt created
[ ] Job class created
[ ] Server class created
[ ] DataCenter class created
[ ] Agent class created
[ ] SimulationConfig class created
[ ] Workload generator created
[ ] Reproducible seed works
[ ] main.py prints workload summary
[ ] README has project idea and motivation
[ ] First Git commit done
```

---

# Day 2 — Simulator Engine and Greedy Schedulers

## Goal

Build the core simulation engine and implement your first scheduling algorithms.

By the end of Day 2, your project should run a full simulation from time `0` to time `T`.

---

## What You Will Learn

You will learn:

```txt
event simulation
priority queues
greedy algorithms
state transitions
metrics tracking
```

This is where the project starts becoming useful for DSA.

---

## Resources to Refer

1. Python heapq documentation  
   https://docs.python.org/3/library/heapq.html

2. Kubernetes kube-scheduler docs  
   https://kubernetes.io/docs/concepts/scheduling-eviction/kube-scheduler/

3. Python argparse documentation  
   https://docs.python.org/3/library/argparse.html

---

## Files to Create or Update

```txt
cloudarena/simulator.py
cloudarena/schedulers.py
cloudarena/metrics.py
main.py
```

---

## Simulation Flow

Your simulator should work like this:

```txt
for each time step:
    add newly arrived jobs to waiting queue
    update running jobs
    mark completed jobs
    release GPU capacity
    call scheduler
    assign selected jobs to servers
    update metrics
```

---

## Job State Transitions

A job starts as:

```txt
WAITING
```

When scheduled:

```txt
RUNNING
```

When runtime is over:

```txt
COMPLETED
```

If the server fails:

```txt
FAILED
```

If it misses deadline before being scheduled:

```txt
REJECTED
```

---

## Base Scheduler Interface

Create a base scheduler:

```python
class Scheduler:
    def schedule(self, jobs, servers, current_time):
        raise NotImplementedError
```

Every scheduler should return assignments like:

```txt
[(job_id, server_id), ...]
```

---

## Schedulers to Implement

Implement:

```txt
FCFSScheduler
EarliestDeadlineFirstScheduler
PriorityScheduler
```

---

## FCFS Scheduler

Schedules jobs by arrival time.

This is your simplest baseline.

Ordering:

```txt
earlier arrival_time first
lower job_id as tie-breaker
```

---

## Earliest Deadline First Scheduler

Schedules jobs by closest deadline.

Ordering:

```txt
earliest deadline first
higher priority second
lower duration third
```

This scheduler is useful because many real workloads are deadline-sensitive.

---

## Priority Scheduler

Schedules important jobs first.

Possible ordering:

```txt
higher priority first
earlier deadline second
lower duration third
```

Use `heapq` for at least one of these schedulers.

---

## Metrics to Track

Create a `Metrics` class that tracks:

```txt
total_jobs
completed_jobs
failed_jobs
rejected_jobs
deadline_misses
average_wait_time
average_completion_time
gpu_utilization
total_cost
```

---

## Day 2 Implementation Steps

1. Create simulator event loop.
2. Add waiting queue.
3. Add running job updates.
4. Release GPU capacity when jobs complete.
5. Implement FCFS scheduler.
6. Implement EDF scheduler.
7. Implement Priority scheduler.
8. Add metrics tracking.
9. Add CLI support for scheduler choice.
10. Run all three schedulers with same seed.
11. Update README with comparison table.
12. Commit code.

---

## Day 2 Deliverable

You should be able to run:

```bash
python main.py --scheduler fcfs --seed 1
python main.py --scheduler edf --seed 1
python main.py --scheduler priority --seed 1
```

Expected output format:

```txt
Scheduler: EDF
Completed jobs: 72/100
Deadline misses: 18
Average wait time: 3.4
GPU utilization: 71.2%
Total cost: 913
```

---

## Day 2 README Update

Add:

```txt
## Baseline Schedulers
### FCFS
### Earliest Deadline First
### Priority Scheduler
```

Also add a small table comparing the first results.

---

## Day 2 Acceptance Checklist

```txt
[ ] Simulator event loop works
[ ] Jobs move through WAITING/RUNNING/COMPLETED states
[ ] Failed and rejected jobs are handled
[ ] FCFS scheduler works
[ ] EDF scheduler works
[ ] Priority scheduler works
[ ] Metrics are printed at the end
[ ] CLI can choose scheduler
[ ] Same seed gives reproducible results
[ ] README contains baseline scheduler explanations
[ ] Git commit done
```

---

# Day 3 — Min-Cost Flow Algorithm from Scratch

## Goal

Implement the core graph algorithm: **min-cost max-flow**.

Do not integrate it into the scheduler yet. First, build and test the algorithm independently.

---

## What You Will Learn

This is the strongest DSA day.

You will learn:

```txt
directed graphs
residual graph
flow
capacity
cost
reverse edges
shortest path
augmenting path
optimization modeling
```

---

## Resources to Refer

1. CP-Algorithms Min Cost Flow  
   https://cp-algorithms.com/graph/min_cost_flow.html

2. USACO Guide Min Cost Flow  
   https://usaco.guide/adv/min-cost-flow

3. Topcoder Minimum Cost Flow tutorial  
   https://www.topcoder.com/community/competitive-programming/tutorials/minimum-cost-flow-part-two-algorithms/

---

## Files to Create

```txt
cloudarena/min_cost_flow.py
tests/test_flow.py
```

---

## Data Structures

Create an `Edge` object with:

```txt
to
rev
capacity
cost
```

Your graph should be represented as:

```txt
graph[u] = list of edges from u
```

When you add an edge `u -> v`, also add a reverse edge `v -> u`.

Forward edge:

```txt
capacity = cap
cost = cost
```

Reverse edge:

```txt
capacity = 0
cost = -cost
```

---

## Algorithm Version

For your project size, implement successive shortest augmenting path.

Simpler version:

```txt
Use Bellman-Ford or SPFA first.
```

After it works, optionally upgrade to:

```txt
Dijkstra with potentials
```

Do not spend the whole day optimizing. Correctness matters more.

---

## Min-Cost Flow API

Create a class like:

```python
class MinCostFlow:
    def __init__(self, n):
        pass

    def add_edge(self, u, v, cap, cost):
        pass

    def min_cost_flow(self, source, sink, max_flow):
        pass
```

Return:

```txt
(flow_sent, total_cost)
```

---

## Minimum Tests

### Test 1 — Simple Path Choice

Graph:

```txt
source -> A cost 1
source -> B cost 5
A -> sink cost 1
B -> sink cost 1
```

Expected minimum cost for sending `1` flow:

```txt
2
```

---

### Test 2 — Two Jobs, Two Servers

Costs:

```txt
job1 -> server1 cost 3
job1 -> server2 cost 8
job2 -> server1 cost 4
job2 -> server2 cost 2
```

Expected assignment:

```txt
job1 -> server1
job2 -> server2
```

Expected cost:

```txt
5
```

---

### Test 3 — No Path Exists

Expected:

```txt
flow = 0
cost = 0
```

---

### Test 4 — Capacity Greater Than 1

Create one server node with capacity `2`.

Expected:

```txt
2 jobs can be assigned to that server
```

---

### Test 5 — Reverse Edge Behavior

Create a case where the first greedy-looking path must be corrected using a reverse edge.

Expected:

```txt
min-cost flow still finds the optimal final cost
```

---

## Day 3 Implementation Steps

1. Implement `Edge` structure.
2. Implement adjacency list graph.
3. Implement `add_edge` with reverse edge.
4. Implement shortest path in residual graph.
5. Implement augmentation.
6. Update capacities correctly.
7. Return flow and cost.
8. Write at least 3 tests.
9. Add more tests if time permits.
10. Update README.
11. Commit code.

---

## Day 3 Deliverable

You should be able to run:

```bash
pytest tests/test_flow.py
```

All flow tests should pass.

---

## Day 3 README Update

Add:

```txt
## Core Algorithm: Min-Cost Max-Flow
```

Explain the graph idea:

```txt
source -> jobs -> servers -> sink
```

Also write rough time complexity.

---

## Day 3 Acceptance Checklist

```txt
[ ] Edge class created
[ ] Reverse edges implemented
[ ] Residual capacities update correctly
[ ] Shortest path logic works
[ ] Min-cost flow returns flow and cost
[ ] At least 3 tests pass
[ ] Ideally 5 tests pass
[ ] README explains the graph idea
[ ] Git commit done
```

---

# Day 4 — Flow-Based Scheduler Integration

## Goal

Use your min-cost flow algorithm to create a realistic optimization scheduler.

By the end of Day 4, your simulator should support:

```bash
python main.py --scheduler flow
```

---

## What You Will Learn

You will learn how to convert a real-world problem into a graph problem.

This is very important for interviews because many hard DSA problems are not directly given as graph problems. You have to model them.

---

## Resources to Refer

1. Microsoft Singularity publication page  
   https://www.microsoft.com/en-us/research/publication/singularity-planet-scale-preemptive-and-elastic-scheduling-of-ai-workloads/

2. Microsoft Research AI Infrastructure page  
   https://www.microsoft.com/en-us/research/project/ai-infrastructure/

3. CP-Algorithms Min Cost Flow  
   https://cp-algorithms.com/graph/min_cost_flow.html

---

## Files to Update

```txt
cloudarena/schedulers.py
cloudarena/min_cost_flow.py
cloudarena/simulator.py
cloudarena/metrics.py
main.py
```

---

## Graph Construction

At each scheduling step, build this graph:

```txt
source -> waiting jobs -> available servers -> sink
```

---

## Source to Job Edges

For every waiting job:

```txt
capacity = 1
cost = 0
```

---

## Job to Server Edges

Only add this edge if the server has enough free GPUs.

```txt
job -> server
capacity = 1
cost = compute_cost(job, server, current_time)
```

---

## Server to Sink Edges

For every server:

```txt
server -> sink
capacity = server.available_gpus
cost = 0
```

---

## Cost Function

Create:

```python
def compute_cost(job, server, current_time):
    pass
```

Possible formula:

```txt
server_cost = server.cost_per_tick * job.duration_mean
latency_cost = server.latency
deadline_penalty = max(0, current_time + job.duration_mean - job.deadline) * 20
failure_penalty = server.failure_probability * job.private_value
priority_bonus = job.priority * 5

total_cost = server_cost + latency_cost + deadline_penalty + failure_penalty - priority_bonus
```

Since min-cost flow can become annoying with negative costs, keep costs non-negative.

Two ways:

```txt
Option 1: reduce priority_bonus so total cost stays non-negative
Option 2: add a constant offset to all job-server edge costs
```

Simpler recommendation:

```txt
total_cost = server_cost + latency_cost + deadline_penalty + failure_penalty + (10 - job.priority)
```

This keeps high-priority jobs cheaper without using negative costs.

---

## Flow Scheduler Return Format

The scheduler should return assignments:

```txt
[(job_id, server_id), ...]
```

Then the simulator should start those jobs.

---

## How to Extract Assignments

After min-cost flow runs, inspect edges from job nodes to server nodes.

If original capacity was `1` and current residual capacity is `0`, that means this edge was used.

Then record:

```txt
job_id assigned to server_id
```

---

## Compare Schedulers

Run the same workload with:

```txt
fcfs
edf
priority
flow
```

Use the same seed.

Commands:

```bash
python main.py --scheduler fcfs --seed 42
python main.py --scheduler edf --seed 42
python main.py --scheduler priority --seed 42
python main.py --scheduler flow --seed 42
```

---

## Example Comparison Table

Your numbers may be different.

```txt
Scheduler   Completed   Deadline Misses   Avg Wait   Utilization   Cost
FCFS        61          31                5.8        63%           820
EDF         70          22                4.1        68%           880
Priority    74          19                3.9        70%           930
Flow        81          12                3.1        77%           790
```

---

## Day 4 Implementation Steps

1. Create `FlowScheduler` class.
2. At each time step, collect waiting jobs.
3. Collect servers with available GPUs.
4. Build graph nodes.
5. Add source-to-job edges.
6. Add job-to-server edges with cost function.
7. Add server-to-sink edges.
8. Run min-cost flow.
9. Extract assignments.
10. Start assigned jobs in simulator.
11. Compare with greedy schedulers.
12. Update README.
13. Commit code.

---

## Day 4 Deliverable

You should be able to run:

```bash
python main.py --scheduler flow --seed 42
```

Expected output format:

```txt
Scheduler: Flow
Completed jobs: 81/100
Deadline misses: 12
Average wait time: 3.1
GPU utilization: 77.0%
Total cost: 790
```

---

## Day 4 README Update

Add:

```txt
## Flow Scheduler
## Cost Function
## Greedy vs Flow Results
```

---

## Day 4 Acceptance Checklist

```txt
[ ] FlowScheduler class created
[ ] Flow scheduler builds graph correctly
[ ] Cost function implemented
[ ] Flow scheduler produces job-server assignments
[ ] Simulator supports --scheduler flow
[ ] Flow results are compared with greedy results
[ ] README has results table
[ ] Git commit done
```

---

# Day 5 — Game Theory and Auction Scheduler

## Goal

Build a scheduler where users compete for GPU slots using bids.

This adds the game-theory part of the project.

---

## What You Will Learn

You will learn:

```txt
private value
bid
utility
truthful strategy
strategic agents
second-price auction
social welfare
cloud revenue
```

---

## Resources to Refer

1. Tim Roughgarden lecture notes on mechanism design  
   https://timroughgarden.org/f13/l/l2.pdf

2. Twenty Lectures on Algorithmic Game Theory  
   https://www.cambridge.org/core/books/twenty-lectures-on-algorithmic-game-theory/A9D9427C8F43E7DAEF8C702755B6D72B

3. Microsoft Azure agentic cloud operations blog  
   https://azure.microsoft.com/en-us/blog/agentic-cloud-operations-a-new-way-to-run-the-cloud/

---

## Files to Create or Update

```txt
cloudarena/auction.py
cloudarena/schedulers.py
cloudarena/models.py
cloudarena/metrics.py
tests/test_auction.py
```

---

## Auction Model

Start simple.

At each time step:

```txt
available GPU slots are auctioned
waiting jobs submit bids
highest bid wins
winner pays second-highest bid
```

For multiple slots, run repeated auctions or assign top jobs one by one.

Do not try to build a perfect real-world cloud pricing model. Keep it understandable.

---

## Auction Rules

For one slot:

```txt
highest bidder wins
winner pays second-highest bid
```

For multiple slots:

```txt
sort bidders by bid descending
top K bidders win
payment can be the next highest losing bid
```

Simpler implementation:

```txt
Run one second-price auction per available GPU slot.
```

---

## Agent Strategies

Implement these strategies.

### Truthful Agent

```txt
bid = private_value
```

### Underbid Agent

```txt
bid = private_value * 0.75
```

### Overbid Agent

```txt
bid = private_value * 1.25
```

### Random Agent

```txt
bid = random value between 0.5 * private_value and 1.5 * private_value
```

### Deadline Panic Agent

```txt
if deadline is close:
    bid = private_value * 1.5
else:
    bid = private_value
```

A possible deadline-close condition:

```txt
job.deadline - current_time <= job.duration_mean + 2
```

---

## Utility Formula

For a winning job:

```txt
utility = private_value - payment - delay_penalty
```

For a losing job:

```txt
utility = 0
```

Delay penalty:

```txt
delay_penalty = max(0, start_time - arrival_time) * penalty_rate
```

---

## Metrics to Add

Add these metrics:

```txt
total_revenue
average_user_utility
social_welfare
truthful_agent_utility
underbid_agent_utility
overbid_agent_utility
random_agent_utility
deadline_panic_agent_utility
```

Social welfare can be:

```txt
sum of private_value of completed jobs - total running cost
```

---

## Tests to Write

### Test 1 — Highest Bidder Wins

Bids:

```txt
A = 100
B = 80
C = 50
```

Expected:

```txt
winner = A
payment = 80
```

---

### Test 2 — Single Bidder

Only one bidder exists.

Choose one rule:

```txt
winner pays reserve price
```

or:

```txt
winner pays 0
```

Pick one and document it.

Recommended simple rule:

```txt
winner pays 0
```

---

### Test 3 — Utility Calculation

Truthful bidder:

```txt
private value = 100
payment = 80
```

Expected utility:

```txt
20
```

assuming delay penalty is `0`.

---

### Test 4 — Underbid Strategy

Private value:

```txt
100
```

Expected bid:

```txt
75
```

---

### Test 5 — Overbid Strategy

Private value:

```txt
100
```

Expected bid:

```txt
125
```

---

## Day 5 Experiments

Run experiments with strategy mixes:

```txt
all truthful
all underbid
all overbid
mixed
```

Compare:

```txt
revenue
average utility
completed jobs
social welfare
```

---

## Day 5 Implementation Steps

1. Create `Auction` class.
2. Add bid calculation for each agent strategy.
3. Implement second-price auction for one slot.
4. Extend to multiple available GPU slots.
5. Create `AuctionScheduler`.
6. Integrate auction scheduler into simulator.
7. Add payment and utility to jobs.
8. Add revenue and welfare metrics.
9. Write auction tests.
10. Run strategy experiments.
11. Update README.
12. Commit code.

---

## Day 5 Deliverable

You should be able to run:

```bash
python main.py --scheduler auction --seed 42
```

Expected output format:

```txt
Scheduler: Auction
Completed jobs: 76/100
Revenue: 4210
Average user utility: 18.4
Social welfare: 13600
```

---

## Day 5 README Update

Add:

```txt
## Auction Scheduler
## Game Theory Model
## Agent Strategies
## Utility and Revenue
```

---

## Day 5 Acceptance Checklist

```txt
[ ] Auction class created
[ ] Truthful strategy implemented
[ ] Underbid strategy implemented
[ ] Overbid strategy implemented
[ ] Random strategy implemented
[ ] Deadline-panic strategy implemented
[ ] AuctionScheduler integrated into simulator
[ ] Payment calculation works
[ ] Utility calculation works
[ ] Revenue metric added
[ ] Social welfare metric added
[ ] Auction tests pass
[ ] README explains second-price auction idea
[ ] Git commit done
```

---

# Day 6 — Probability, Uncertainty, and Monte Carlo Simulation

## Goal

Make the simulator realistic by adding uncertainty.

By the end of Day 6, your results should not come from only one run. They should come from many repeated simulations.

---

## What You Will Learn

You will learn:

```txt
random variables
Bernoulli trials
runtime uncertainty
failure probability
expected value
Monte Carlo simulation
mean and variance
reproducibility with seeds
```

---

## Resources to Refer

1. Python random module documentation  
   https://docs.python.org/3/library/random.html

2. Python csv module documentation  
   https://docs.python.org/3/library/csv.html

3. Matplotlib quick start  
   https://matplotlib.org/stable/users/explain/quick_start.html

---

## Files to Create or Update

```txt
cloudarena/probability.py
cloudarena/metrics.py
cloudarena/simulator.py
main.py
results/monte_carlo_results.csv
```

---

## Add Uncertain Runtime

Instead of every job taking exactly `duration_mean`, sample actual runtime.

Simple version:

```txt
actual_duration = random integer around duration_mean
```

Better version:

```txt
actual_duration = lognormal or normal-like random value
```

Keep it bounded:

```txt
actual_duration = max(1, sampled_duration)
```

Example rule:

```txt
actual_duration = max(1, int(random.gauss(duration_mean, duration_std)))
```

---

## Add Server Failures

Each server has:

```txt
failure_probability
```

When a job is running, each time step can have a small chance of failure.

Simple rule:

```txt
if random() < server.failure_probability:
    job fails
    release GPU
```

This is a Bernoulli trial.

---

## Add Random Job Arrivals

You already generated arrival times on Day 1.

Improve them by using random distributions:

```txt
uniform arrivals
burst arrivals
peak-hour arrivals
```

Simple implementation:

```txt
most jobs arrive between time 0 and time_horizon / 2
some jobs arrive later
```

---

## Add Monte Carlo Runner

Create:

```python
def run_monte_carlo(scheduler_name, runs, config):
    pass
```

It should run the same scheduler many times with different seeds.

Example command:

```bash
python main.py --scheduler flow --runs 100
```

Expected output:

```txt
Scheduler: Flow
Runs: 100
Average completed jobs: 81.4
Average deadline misses: 12.7
Average utilization: 78.2%
Average cost: 812.5
```

---

## Save Results

Save CSV like:

```txt
results/monte_carlo_results.csv
```

Columns:

```txt
run_id
scheduler
completed_jobs
failed_jobs
rejected_jobs
deadline_misses
average_wait_time
average_completion_time
gpu_utilization
total_cost
revenue
average_user_utility
social_welfare
```

---

## Day 6 Experiments

Run all schedulers:

```txt
fcfs
edf
priority
flow
auction
```

For each scheduler, run:

```txt
30 runs minimum
100 runs ideal
```

Commands:

```bash
python main.py --scheduler fcfs --runs 30
python main.py --scheduler edf --runs 30
python main.py --scheduler priority --runs 30
python main.py --scheduler flow --runs 30
python main.py --scheduler auction --runs 30
```

---

## Metrics to Average

Average these across runs:

```txt
completed_jobs
deadline_misses
average_wait_time
average_completion_time
gpu_utilization
total_cost
revenue
average_user_utility
social_welfare
```

Also calculate standard deviation for at least:

```txt
completed_jobs
deadline_misses
gpu_utilization
```

---

## Day 6 Implementation Steps

1. Create `probability.py`.
2. Add runtime sampling.
3. Add server failure sampling.
4. Add stochastic job arrival improvements.
5. Add Monte Carlo runner.
6. Add CSV export.
7. Add averaging logic.
8. Add standard deviation for important metrics.
9. Run 30 experiments per scheduler.
10. Update README with results table.
11. Commit code.

---

## Day 6 README Update

Add:

```txt
## Stochastic Simulation
## Monte Carlo Evaluation
```

Add a table:

```txt
Scheduler   Avg Completed   Avg Misses   Avg Utilization   Avg Cost
FCFS        ...
EDF         ...
Priority    ...
Flow        ...
Auction     ...
```

---

## Day 6 Acceptance Checklist

```txt
[ ] Runtime randomness added
[ ] Server failure randomness added
[ ] Random job arrivals improved
[ ] Monte Carlo runner works
[ ] Results saved to CSV
[ ] At least 30 runs per scheduler completed
[ ] Averages calculated
[ ] Standard deviations calculated for key metrics
[ ] README includes Monte Carlo results
[ ] Git commit done
```

---

# Day 7 — Dashboard and Visualizations

## Goal

Create a visual demo using Streamlit.

This is what makes the project attractive to recruiters because they can understand it quickly.

---

## What You Will Learn

You will learn:

```txt
data visualization
dashboard design
experiment comparison
interactive controls
communicating algorithms visually
```

---

## Resources to Refer

1. Streamlit Get Started documentation  
   https://docs.streamlit.io/get-started

2. Streamlit create-an-app tutorial  
   https://docs.streamlit.io/get-started/tutorials/create-an-app

3. Matplotlib quick start  
   https://matplotlib.org/stable/users/explain/quick_start.html

---

## Files to Create

```txt
app.py
screenshots/dashboard.png
```

---

## Dashboard Sections

Create these sections:

```txt
Project Overview
Scheduler Selection
Simulation Config
Results Table
Scheduler Comparison Charts
Auction Analysis
Flow Scheduler Explanation
```

---

## Dashboard Controls

Add controls for:

```txt
number of jobs
number of servers
number of users
scheduler
random seed
failure probability level
number of Monte Carlo runs
```

---

## Charts to Show

Show at least these charts.

### Chart 1 — Completed Jobs by Scheduler

Purpose:

```txt
Shows which scheduler finishes the most work.
```

---

### Chart 2 — Deadline Misses by Scheduler

Purpose:

```txt
Shows which scheduler handles deadlines better.
```

---

### Chart 3 — GPU Utilization by Scheduler

Purpose:

```txt
Shows how well each scheduler uses hardware.
```

---

### Chart 4 — Total Cost by Scheduler

Purpose:

```txt
Shows cost efficiency.
```

---

### Chart 5 — Auction Revenue by Agent Strategy

Purpose:

```txt
Shows the game-theoretic behavior of different bidding strategies.
```

---

## Important Dashboard Rule

Do not overbuild the UI.

The dashboard should answer these questions:

```txt
Which scheduler completed the most jobs?
Which scheduler missed fewer deadlines?
Which scheduler used GPUs better?
Which scheduler had lower cost?
How did auction strategies affect revenue and utility?
```

---

## Day 7 Implementation Steps

1. Create `app.py`.
2. Add Streamlit title and project overview.
3. Add sidebar controls.
4. Run one simulation from the dashboard.
5. Add result table.
6. Add scheduler comparison mode.
7. Add charts.
8. Add auction section.
9. Add flow scheduler explanation.
10. Take screenshots.
11. Add screenshots to README.
12. Commit code.

---

## Day 7 Deliverable

You should be able to run:

```bash
streamlit run app.py
```

And interactively compare schedulers.

---

## Day 7 README Update

Add:

```txt
## Dashboard
## Screenshots
```

Take 2-3 screenshots and add them to README.

---

## Day 7 Acceptance Checklist

```txt
[ ] Streamlit app runs
[ ] User can choose scheduler
[ ] User can change simulation parameters
[ ] Results table appears
[ ] Completed jobs chart appears
[ ] Deadline misses chart appears
[ ] GPU utilization chart appears
[ ] Cost chart appears
[ ] Auction revenue chart appears
[ ] Screenshots added to README
[ ] Git commit done
```

---

# Day 8 — Testing, Cleanup, CLI, and README Polish

## Goal

Make the project look professional.

This day is not about adding major features. It is about making the project reliable and presentable.

---

## What You Will Learn

You will learn:

```txt
unit testing
clean CLI design
reproducible experiments
documentation
project packaging
```

---

## Resources to Refer

1. pytest Get Started documentation  
   https://docs.pytest.org/en/stable/getting-started.html

2. Python argparse documentation  
   https://docs.python.org/3/library/argparse.html

3. Python csv documentation  
   https://docs.python.org/3/library/csv.html

---

## Tests to Write

### tests/test_flow.py

Test:

```txt
minimum cost is correct
no path case works
capacity greater than 1 works
reverse edges update correctly
```

---

### tests/test_auction.py

Test:

```txt
highest bidder wins
winner pays second highest bid
utility calculation is correct
single bidder case works
underbid strategy works
overbid strategy works
```

---

### tests/test_greedy.py

Test:

```txt
EDF chooses earliest deadline
priority scheduler chooses highest priority
scheduler does not assign job to full server
FCFS respects arrival order
```

---

### tests/test_metrics.py

Test:

```txt
completed jobs counted correctly
deadline misses counted correctly
average wait time calculated correctly
GPU utilization is between 0 and 100
revenue is counted correctly
social welfare is calculated correctly
```

---

## CLI Commands to Support

Your `main.py` should support:

```bash
python main.py --scheduler flow --seed 42
python main.py --scheduler auction --seed 42
python main.py --scheduler flow --runs 100
python main.py --compare-all --runs 50
python main.py --jobs 200 --servers 20 --seed 7
```

Optional:

```bash
python main.py --export results/custom_results.csv
python main.py --strategy-mix mixed
```

---

## README Final Structure

Your README should contain:

```txt
# CloudArena

## 1. Problem Statement
## 2. Why This Project Matters
## 3. Real-World Inspiration
## 4. Features
## 5. System Architecture
## 6. Algorithms Implemented
## 7. OOP Design
## 8. Probability Model
## 9. Game Theory Model
## 10. Results
## 11. Dashboard Screenshots
## 12. How to Run
## 13. Tests
## 14. Future Improvements
```

---

## Results Section

Include a table like this:

```txt
Scheduler   Completed   Misses   Utilization   Cost   Revenue   Welfare
FCFS        ...         ...      ...           ...    ...       ...
EDF         ...         ...      ...           ...    ...       ...
Priority    ...         ...      ...           ...    ...       ...
Flow        ...         ...      ...           ...    ...       ...
Auction     ...         ...      ...           ...    ...       ...
```

Then add a short explanation:

```txt
Flow scheduler performed better on deadline misses because it globally optimized job-server assignment instead of making local greedy choices.

Auction scheduler produced revenue and utility metrics, making it useful when users are strategic and GPU capacity is scarce.
```

---

## Day 8 Implementation Steps

1. Write tests for flow.
2. Write tests for auction.
3. Write tests for greedy schedulers.
4. Write tests for metrics.
5. Clean CLI.
6. Add `--compare-all` command.
7. Add result export.
8. Fix broken imports.
9. Run full test suite.
10. Run final experiments.
11. Update README fully.
12. Add screenshots.
13. Commit code.

---

## Day 8 Deliverable

You should be able to run:

```bash
pytest
python main.py --compare-all --runs 30
streamlit run app.py
```

All should work.

---

## Day 8 Acceptance Checklist

```txt
[ ] At least 15-20 tests pass
[ ] CLI is clean
[ ] README is complete
[ ] Screenshots are added
[ ] Results are reproducible
[ ] No broken imports
[ ] Project can be run by another person using README
[ ] --compare-all works
[ ] pytest works
[ ] streamlit app works
[ ] Git commit done
```

---

# Day 9 — Final Polish, Optional C++ Core, Resume, and Demo

## Goal

Turn the project from working code into an internship-ready portfolio project.

This is your polish day.

---

## What You Will Learn

You will learn:

```txt
performance comparison
technical storytelling
resume writing
demo preparation
interview explanation
```

---

## Resources to Refer

Only use the C++ resources if you choose to implement the optional C++ min-cost flow version.

1. C++ `std::priority_queue` reference  
   https://en.cppreference.com/w/cpp/container/priority_queue

2. C++ `std::vector` reference  
   https://en.cppreference.com/w/cpp/container/vector

3. C++ random library reference  
   https://en.cppreference.com/w/cpp/numeric/random

---

## Option A — Python-Only Polish

Do this if your project still needs cleanup.

Tasks:

```txt
fix bugs
clean folder structure
improve README
add more screenshots
add better chart labels
make sample results reproducible
write short architecture explanation
record 2-minute demo video
```

---

## Option B — Add C++ Min-Cost Flow Core

Do this only after the Python project is complete.

Create:

```txt
cpp/min_cost_flow.cpp
```

Implement the same min-cost flow algorithm in C++.

Then add a README note:

```txt
The optimization core was also implemented in C++ to demonstrate lower-level DSA implementation.
```

Do not try to connect C++ to Python unless you have extra time. A standalone C++ file is enough.

---

## Demo Video Script

Record a short demo:

```txt
0:00 - 0:20    What problem CloudArena solves
0:20 - 0:50    Show simulator and schedulers
0:50 - 1:20    Show flow scheduler result
1:20 - 1:50    Show auction/game theory result
1:50 - 2:20    Show dashboard
2:20 - 2:40    Explain what you learned
```

---

## Resume Bullets

Use bullets like these:

```txt
Built CloudArena, a GPU cloud workload scheduling simulator comparing greedy, min-cost flow, and auction-based allocation strategies under stochastic failures and runtime uncertainty.
```

```txt
Implemented min-cost max-flow from scratch to optimize job-to-server assignment using cost, latency, deadline penalties, and failure risk.
```

```txt
Designed a game-theoretic auction scheduler with truthful, underbidding, overbidding, and deadline-panic agents; measured revenue, social welfare, and user utility.
```

```txt
Created Monte Carlo experiments and a Streamlit dashboard to compare scheduler performance across completion rate, deadline misses, GPU utilization, and cost.
```

---

## Interview Explanation

Prepare this answer:

```txt
CloudArena simulates a cloud GPU cluster where users submit jobs with deadlines, budgets, and private values. I implemented multiple schedulers: greedy baselines, a min-cost flow optimizer, and an auction-based scheduler. The project combines DSA, OOP, probability, and game theory. I evaluated all schedulers using Monte Carlo simulation under uncertain runtimes and server failures, then built a dashboard to compare metrics.
```

---

## Day 9 Implementation Steps

1. Fix remaining bugs.
2. Clean final README.
3. Add final screenshots.
4. Add final results table.
5. Write resume bullets.
6. Prepare demo script.
7. Optionally implement C++ min-cost flow.
8. Run final tests.
9. Run dashboard.
10. Pin GitHub repository.
11. Commit final version.

---

## Day 9 Acceptance Checklist

```txt
[ ] README looks professional
[ ] Demo screenshots added
[ ] Resume bullets written
[ ] Demo video recorded or script prepared
[ ] Optional C++ core completed if time permits
[ ] GitHub repo pinned
[ ] Final tests pass
[ ] Final commit done
```

---

# 8-Day Adjustment

For an 8-day version, merge Day 8 and Day 9.

That means:

```txt
Day 8 morning: tests and README
Day 8 afternoon: screenshots, resume bullets, final polish
```

Skip the C++ core unless everything else is already complete.

The Python version with strong algorithms, clean explanation, tests, dashboard, and README is enough for a serious internship portfolio project.

---

# What to Prioritize if You Fall Behind

Do not try to build everything equally. Prioritize in this order:

```txt
1. OOP models and workload generator
2. Simulator engine
3. Greedy schedulers
4. Min-cost flow scheduler
5. Monte Carlo results
6. README
7. Dashboard
8. Auction scheduler
9. Optional C++ core
```

The most internship-impressive parts are:

```txt
min-cost flow from scratch
clean OOP design
Monte Carlo evaluation
clear README with results
dashboard screenshots
```

---

# Suggested Git Commit Plan

Use meaningful commits:

```txt
Day 1: init project with OOP models and workload generator
Day 2: add simulator and greedy schedulers
Day 3: implement min-cost flow from scratch
Day 4: integrate flow scheduler into simulator
Day 5: add auction scheduler and agent strategies
Day 6: add stochastic simulation and Monte Carlo runner
Day 7: add Streamlit dashboard and visualizations
Day 8: add tests, CLI cleanup, and README polish
Day 9: final polish and optional C++ min-cost flow
```

---

# Suggested README Summary

Use this near the top of your README:

```txt
CloudArena is a GPU cloud workload scheduling simulator. It compares greedy scheduling, min-cost flow optimization, and auction-based resource allocation under stochastic runtime uncertainty and server failures. The project demonstrates data structures and algorithms, OOP design, probability, and game theory in one realistic system.
```

---

# Suggested Feature List for README

```txt
- Object-oriented simulation of jobs, servers, agents, and data centers
- FCFS, earliest-deadline-first, and priority greedy schedulers
- Min-cost max-flow scheduler implemented from scratch
- Auction-based scheduler with strategic bidding agents
- Runtime uncertainty and server failure simulation
- Monte Carlo evaluation across repeated runs
- Metrics for completion rate, deadline misses, GPU utilization, cost, revenue, utility, and social welfare
- CSV export for experiment results
- Streamlit dashboard for interactive comparison
- Unit tests for algorithms, auctions, schedulers, and metrics
```

---

# Suggested Future Improvements

Add this to the README if you want:

```txt
- Support multi-GPU jobs
- Add preemptive scheduling
- Add job migration between servers
- Use Dijkstra with potentials for faster min-cost flow
- Add reinforcement-learning based scheduler
- Add real cluster trace input
- Add Kubernetes-style scheduler plugins
- Add fairness constraints between users
- Add carbon-aware scheduling using energy cost per data center
```

---

# Final Success Criteria

Your project is internship-ready when:

```txt
[ ] A recruiter can understand the project from README in under 2 minutes
[ ] The project runs with one or two commands
[ ] The algorithms are implemented by you, not hidden inside libraries
[ ] The results are reproducible using seeds
[ ] The dashboard shows clear comparisons
[ ] The project has tests
[ ] The resume bullets sound technical and measurable
[ ] You can explain the architecture in an interview
```

---

# Final Advice

Focus on finishing a clean, working version rather than adding too many features.

The best version is not the largest version. The best version is the one that:

```txt
runs correctly
has strong algorithms
has clear explanations
has visual results
has tests
has a professional README
```

CloudArena is strong because it connects interview-level DSA with real-world cloud and AI infrastructure problems.
