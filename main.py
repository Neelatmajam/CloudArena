import argparse

from cloudarena.monte_carlo import (
    MONTE_CARLO_SCHEDULERS,
    run_monte_carlo,
    summarize_results,
    write_monte_carlo_csv,
)
from cloudarena.models import SimulationConfig
from cloudarena.schedulers import create_scheduler
from cloudarena.simulator import Simulator
from cloudarena.workload import generate_workload


def parse_args():
    parser = argparse.ArgumentParser(description="Run the CloudArena simulator.")
    parser.add_argument(
        "--scheduler",
        choices=["fcfs", "edf", "priority", "flow"],
        default="fcfs",
        help="Scheduling strategy to use.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--jobs", type=int, default=None)
    parser.add_argument("--servers", type=int, default=None)
    parser.add_argument("--agents", type=int, default=None)
    parser.add_argument("--data-centers", type=int, default=None)
    parser.add_argument("--time-horizon", type=int, default=None)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--compare-all", action="store_true")
    parser.add_argument("--export", default="results/monte_carlo_results.csv")
    parser.add_argument("--failure-probability", type=float, default=None)
    parser.add_argument(
        "--deterministic-runtime",
        action="store_true",
        help="Disable stochastic runtime sampling.",
    )
    return parser.parse_args()


def build_config(args) -> SimulationConfig:
    defaults = SimulationConfig(seed=args.seed)
    return SimulationConfig(
        num_jobs=args.jobs if args.jobs is not None else defaults.num_jobs,
        num_servers=args.servers if args.servers is not None else defaults.num_servers,
        num_agents=args.agents if args.agents is not None else defaults.num_agents,
        num_data_centers=(
            args.data_centers
            if args.data_centers is not None
            else defaults.num_data_centers
        ),
        time_horizon=(
            args.time_horizon
            if args.time_horizon is not None
            else defaults.time_horizon
        ),
        seed=args.seed,
        default_failure_probability=(
            args.failure_probability
            if args.failure_probability is not None
            else defaults.default_failure_probability
        ),
        runtime_uncertainty=not args.deterministic_runtime,
    )


def main():
    args = parse_args()
    config = build_config(args)

    if args.runs > 1 or args.compare_all:
        scheduler_names = (
            MONTE_CARLO_SCHEDULERS
            if args.compare_all
            else (args.scheduler,)
        )
        all_runs = []

        for scheduler_name in scheduler_names:
            runs = run_monte_carlo(scheduler_name, args.runs, config)
            all_runs.extend(runs)
            summary = summarize_results(runs)

            for line in summary.summary_lines():
                print(line)
            print()

        output_path = write_monte_carlo_csv(args.export, all_runs)
        print(f"Saved Monte Carlo results to {output_path}")
        return

    jobs, servers, agents, data_centers = generate_workload(config, config.seed)

    print(f"Generated {len(jobs)} jobs")
    print(f"Generated {len(servers)} servers")
    print(f"Generated {len(agents)} users")
    print(f"Generated {len(data_centers)} data centers")
    print()

    scheduler = create_scheduler(args.scheduler)
    simulator = Simulator(jobs, servers, scheduler, config, seed=config.seed)
    metrics = simulator.run()

    for line in metrics.summary_lines(args.scheduler):
        print(line)


if __name__ == "__main__":
    main()
