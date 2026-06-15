from cloudarena.models import Job, Server
from cloudarena.schedulers import (
    EarliestDeadlineFirstScheduler,
    FCFSScheduler,
    PriorityScheduler,
)


def make_job(
    job_id,
    arrival_time=0,
    deadline=10,
    duration_mean=3,
    priority=1,
    gpu_required=1,
):
    return Job(
        job_id=job_id,
        user_id=0,
        arrival_time=arrival_time,
        deadline=deadline,
        duration_mean=duration_mean,
        duration_std=1,
        gpu_required=gpu_required,
        budget=100,
        private_value=150,
        priority=priority,
        region="us-east",
    )


def make_server(available_gpus=1):
    return Server(
        server_id=0,
        data_center_id=0,
        region="us-east",
        gpu_capacity=1,
        available_gpus=available_gpus,
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=10,
    )


def test_fcfs_respects_arrival_order():
    jobs = [
        make_job(1, arrival_time=5),
        make_job(2, arrival_time=1),
    ]

    assignments = FCFSScheduler().schedule(jobs, [make_server()], current_time=5)

    assert assignments == [(2, 0)]


def test_edf_chooses_earliest_deadline():
    jobs = [
        make_job(1, deadline=20),
        make_job(2, deadline=8),
    ]

    assignments = EarliestDeadlineFirstScheduler().schedule(
        jobs,
        [make_server()],
        current_time=0,
    )

    assert assignments == [(2, 0)]


def test_priority_scheduler_chooses_highest_priority():
    jobs = [
        make_job(1, priority=1),
        make_job(2, priority=5),
    ]

    assignments = PriorityScheduler().schedule(jobs, [make_server()], current_time=0)

    assert assignments == [(2, 0)]


def test_scheduler_does_not_assign_to_full_server():
    jobs = [make_job(1)]

    assignments = FCFSScheduler().schedule(
        jobs,
        [make_server(available_gpus=0)],
        current_time=0,
    )

    assert assignments == []
