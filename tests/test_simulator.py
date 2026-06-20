from cloudarena.models import SimulationConfig
from cloudarena.schedulers import FCFSScheduler
from cloudarena.simulator import Simulator


def test_simulator_records_five_status_timelines(job_factory, server_factory):
    jobs = [
        job_factory(1, arrival_time=0, duration=2),
        job_factory(2, arrival_time=1, duration=2),
    ]
    simulator = Simulator(
        jobs=jobs,
        servers=[server_factory()],
        scheduler=FCFSScheduler(),
        config=SimulationConfig(time_horizon=10),
        seed=1,
    )

    simulator.run()

    assert set(simulator.timelines) == {
        "waiting",
        "running",
        "completed",
        "failed",
        "rejected",
    }
    assert all(simulator.timelines[name] for name in simulator.timelines)
    assert simulator.timelines["running"][0] == {"time": 0, "job_ids": [1]}
    assert simulator.timelines["waiting"][1] == {"time": 1, "job_ids": [2]}
    assert simulator.timelines["completed"][-1]["job_ids"] == [1, 2]
