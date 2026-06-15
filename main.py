import argparse

from cloudarena.models import SimulationConfig
from cloudarena.schedulers import create_scheduler
from cloudarena.simulator import Simulator
from cloudarena.workload import generate_workload


def parse_args():
    parser = argparse.ArgumentParser(description="Run the CloudArena simulator.")
    parser.add_argument(
        "--scheduler",
        choices=["fcfs", "edf", "priority"],
        default="fcfs",
        help="Scheduling strategy to use.",
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--jobs", type=int, default=None)
    parser.add_argument("--servers", type=int, default=None)
    parser.add_argument("--agents", type=int, default=None)
    parser.add_argument("--data-centers", type=int, default=None)
    parser.add_argument("--time-horizon", type=int, default=None)
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
        default_failure_probability=defaults.default_failure_probability,
        runtime_uncertainty=defaults.runtime_uncertainty,
    )


def main():
    args = parse_args()
    config = build_config(args)

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
