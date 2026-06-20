import csv
from dataclasses import dataclass, replace
from pathlib import Path
from statistics import mean, pstdev

from cloudarena.metrics import Metrics
from cloudarena.models import SimulationConfig
from cloudarena.schedulers import create_scheduler
from cloudarena.simulator import Simulator
from cloudarena.workload import generate_workload


MONTE_CARLO_SCHEDULERS = ("fcfs", "edf", "priority", "flow")


@dataclass
class MonteCarloRun:
    run_id: int
    scheduler: str
    seed: int
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    rejected_jobs: int
    deadline_misses: int
    average_wait_time: float
    average_completion_time: float
    gpu_utilization: float
    total_cost: float

    @classmethod
    def from_metrics(
        cls,
        run_id: int,
        scheduler: str,
        seed: int,
        metrics: Metrics,
    ) -> "MonteCarloRun":
        return cls(
            run_id=run_id,
            scheduler=scheduler,
            seed=seed,
            total_jobs=metrics.total_jobs,
            completed_jobs=metrics.completed_jobs,
            failed_jobs=metrics.failed_jobs,
            rejected_jobs=metrics.rejected_jobs,
            deadline_misses=metrics.deadline_misses,
            average_wait_time=round(metrics.average_wait_time, 4),
            average_completion_time=round(metrics.average_completion_time, 4),
            gpu_utilization=round(metrics.gpu_utilization, 4),
            total_cost=round(metrics.total_cost, 2),
        )


@dataclass
class MonteCarloSummary:
    scheduler: str
    runs: int
    average_completed_jobs: float
    average_failed_jobs: float
    average_rejected_jobs: float
    average_deadline_misses: float
    average_wait_time: float
    average_completion_time: float
    average_gpu_utilization: float
    average_total_cost: float
    std_completed_jobs: float
    std_deadline_misses: float
    std_gpu_utilization: float

    def summary_lines(self) -> list[str]:
        return [
            f"Scheduler: {self.scheduler.upper()}",
            f"Runs: {self.runs}",
            f"Average completed jobs: {self.average_completed_jobs:.2f}",
            f"Average failed jobs: {self.average_failed_jobs:.2f}",
            f"Average rejected jobs: {self.average_rejected_jobs:.2f}",
            f"Average deadline misses: {self.average_deadline_misses:.2f}",
            f"Average wait time: {self.average_wait_time:.2f}",
            f"Average completion time: {self.average_completion_time:.2f}",
            f"Average GPU utilization: {self.average_gpu_utilization:.1f}%",
            f"Average total cost: {self.average_total_cost:.2f}",
            f"Std completed jobs: {self.std_completed_jobs:.2f}",
            f"Std deadline misses: {self.std_deadline_misses:.2f}",
            f"Std GPU utilization: {self.std_gpu_utilization:.2f}",
        ]


def run_single_simulation(
    scheduler_name: str,
    config: SimulationConfig,
    seed: int,
    run_id: int = 0,
) -> MonteCarloRun:
    run_config = replace(config, seed=seed)
    jobs, servers, _, _ = generate_workload(run_config, seed)
    scheduler = create_scheduler(scheduler_name)
    simulator = Simulator(jobs, servers, scheduler, run_config, seed=seed)
    metrics = simulator.run()

    return MonteCarloRun.from_metrics(run_id, scheduler_name, seed, metrics)


def run_monte_carlo(
    scheduler_name: str,
    runs: int,
    config: SimulationConfig,
) -> list[MonteCarloRun]:
    if runs <= 0:
        raise ValueError("Monte Carlo runs must be positive.")

    return [
        run_single_simulation(
            scheduler_name,
            config,
            seed=config.seed + run_id,
            run_id=run_id,
        )
        for run_id in range(runs)
    ]


def summarize_results(runs: list[MonteCarloRun]) -> MonteCarloSummary:
    if not runs:
        raise ValueError("Cannot summarize an empty Monte Carlo result set.")

    scheduler = runs[0].scheduler
    return MonteCarloSummary(
        scheduler=scheduler,
        runs=len(runs),
        average_completed_jobs=_average([run.completed_jobs for run in runs]),
        average_failed_jobs=_average([run.failed_jobs for run in runs]),
        average_rejected_jobs=_average([run.rejected_jobs for run in runs]),
        average_deadline_misses=_average([run.deadline_misses for run in runs]),
        average_wait_time=_average([run.average_wait_time for run in runs]),
        average_completion_time=_average(
            [run.average_completion_time for run in runs]
        ),
        average_gpu_utilization=_average([run.gpu_utilization for run in runs]),
        average_total_cost=_average([run.total_cost for run in runs]),
        std_completed_jobs=_std([run.completed_jobs for run in runs]),
        std_deadline_misses=_std([run.deadline_misses for run in runs]),
        std_gpu_utilization=_std([run.gpu_utilization for run in runs]),
    )


def write_monte_carlo_csv(path: str | Path, runs: list[MonteCarloRun]) -> Path:
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=list(MonteCarloRun.__annotations__))
        writer.writeheader()
        for run in runs:
            writer.writerow(run.__dict__)

    return output_path


def _average(values: list[float]) -> float:
    return round(mean(values), 4)


def _std(values: list[float]) -> float:
    return round(pstdev(values), 4)
