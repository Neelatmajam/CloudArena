from cloudarena.schedulers import (
    EarliestDeadlineFirstScheduler,
    FCFSScheduler,
    PriorityScheduler,
)


def test_fcfs_respects_arrival_order(job_factory, server_factory):
    jobs = [
        job_factory(1, arrival_time=5),
        job_factory(2, arrival_time=1),
    ]

    assignments = FCFSScheduler().schedule(jobs, [server_factory()], current_time=5)

    assert assignments == [(2, 0)]


def test_edf_chooses_earliest_deadline(job_factory, server_factory):
    jobs = [
        job_factory(1, deadline=20),
        job_factory(2, deadline=8),
    ]

    assignments = EarliestDeadlineFirstScheduler().schedule(
        jobs,
        [server_factory()],
        current_time=0,
    )

    assert assignments == [(2, 0)]


def test_priority_scheduler_chooses_highest_priority(job_factory, server_factory):
    jobs = [
        job_factory(1, priority=1),
        job_factory(2, priority=5),
    ]

    assignments = PriorityScheduler().schedule(
        jobs,
        [server_factory()],
        current_time=0,
    )

    assert assignments == [(2, 0)]


def test_scheduler_does_not_assign_to_full_server(job_factory, server_factory):
    jobs = [job_factory(1)]

    assignments = FCFSScheduler().schedule(
        jobs,
        [server_factory(available_gpus=0)],
        current_time=0,
    )

    assert assignments == []
