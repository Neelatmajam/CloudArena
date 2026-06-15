from cloudarena.models import Job, Server, SimulationConfig
from cloudarena.schedulers import FCFSScheduler
from cloudarena.simulator import Simulator


def make_job(job_id, arrival_time=0, deadline=10, duration_mean=2):
    return Job(
        job_id=job_id,
        user_id=0,
        arrival_time=arrival_time,
        deadline=deadline,
        duration_mean=duration_mean,
        duration_std=1,
        gpu_required=1,
        budget=100,
        private_value=150,
        priority=1,
        region="us-east",
    )


def make_server():
    return Server(
        server_id=0,
        data_center_id=0,
        region="us-east",
        gpu_capacity=1,
        available_gpus=1,
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=10,
    )


def test_simulator_records_five_status_timelines():
    jobs = [
        make_job(1, arrival_time=0),
        make_job(2, arrival_time=1),
    ]
    simulator = Simulator(
        jobs=jobs,
        servers=[make_server()],
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
