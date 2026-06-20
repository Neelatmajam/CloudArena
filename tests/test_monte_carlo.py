from pathlib import Path

from cloudarena.models import SimulationConfig
from cloudarena.monte_carlo import (
    run_monte_carlo,
    summarize_results,
    write_monte_carlo_csv,
)


def test_run_monte_carlo_uses_one_seed_per_run():
    config = SimulationConfig(
        num_jobs=6,
        num_servers=2,
        num_agents=2,
        num_data_centers=1,
        time_horizon=20,
        seed=10,
        default_failure_probability=0.0,
    )

    runs = run_monte_carlo("fcfs", 3, config)

    assert [run.run_id for run in runs] == [0, 1, 2]
    assert [run.seed for run in runs] == [10, 11, 12]
    assert all(run.scheduler == "fcfs" for run in runs)


def test_summarize_results_calculates_averages_and_std():
    config = SimulationConfig(
        num_jobs=6,
        num_servers=2,
        num_agents=2,
        num_data_centers=1,
        time_horizon=20,
        seed=20,
        default_failure_probability=0.0,
    )
    runs = run_monte_carlo("priority", 4, config)

    summary = summarize_results(runs)

    assert summary.scheduler == "priority"
    assert summary.runs == 4
    assert 0 <= summary.average_completed_jobs <= config.num_jobs
    assert summary.std_completed_jobs >= 0
    assert summary.std_deadline_misses >= 0
    assert summary.std_gpu_utilization >= 0


def test_write_monte_carlo_csv_creates_export(tmp_path: Path):
    config = SimulationConfig(
        num_jobs=4,
        num_servers=1,
        num_agents=1,
        num_data_centers=1,
        time_horizon=15,
        seed=30,
        default_failure_probability=0.0,
    )
    runs = run_monte_carlo("edf", 2, config)

    output_path = write_monte_carlo_csv(tmp_path / "results.csv", runs)

    text = output_path.read_text()
    assert "run_id,scheduler,seed" in text
    assert "edf" in text
