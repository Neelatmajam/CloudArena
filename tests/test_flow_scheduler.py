from cloudarena.schedulers import FlowScheduler, create_scheduler


def test_create_scheduler_supports_flow():
    scheduler = create_scheduler("flow")

    assert isinstance(scheduler, FlowScheduler)


def test_flow_scheduler_prefers_region_matched_assignment(
    job_factory,
    server_factory,
):
    jobs = [
        job_factory(1, region="us-east"),
        job_factory(2, region="europe"),
    ]
    servers = [
        server_factory(server_id=0, region="us-east", latency=1),
        server_factory(server_id=1, region="europe", latency=1),
    ]

    assignments = FlowScheduler().schedule(jobs, servers, current_time=0)

    assert assignments == [(1, 0), (2, 1)]


def test_flow_scheduler_does_not_return_gpu_overallocation(
    job_factory,
    server_factory,
):
    jobs = [
        job_factory(1, gpu_required=2),
        job_factory(2, gpu_required=2),
    ]
    servers = [
        server_factory(server_id=0, gpu_capacity=2, available_gpus=2),
    ]

    assignments = FlowScheduler().schedule(jobs, servers, current_time=0)

    assert len(assignments) == 1
    assert assignments[0][1] == 0


def test_flow_scheduler_skips_servers_without_enough_gpus(
    job_factory,
    server_factory,
):
    jobs = [job_factory(1, gpu_required=2)]
    servers = [
        server_factory(server_id=0, gpu_capacity=1, available_gpus=1),
    ]

    assignments = FlowScheduler().schedule(jobs, servers, current_time=0)

    assert assignments == []


def test_flow_cost_is_non_negative_and_rewards_priority(
    job_factory,
    server_factory,
):
    server = server_factory()
    low_priority = job_factory(1, priority=1)
    high_priority = job_factory(2, priority=5)

    low_cost = FlowScheduler.compute_cost(low_priority, server, current_time=0)
    high_cost = FlowScheduler.compute_cost(high_priority, server, current_time=0)

    assert low_cost >= 0
    assert high_cost >= 0
    assert high_cost < low_cost
