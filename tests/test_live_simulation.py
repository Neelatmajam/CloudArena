from cloudarena.live_simulation import LiveSimulation


def test_live_simulation_assigns_waiting_job_to_server():
    simulation = LiveSimulation()
    simulation.add_data_center("us-east", energy_cost=1.0, base_latency=5)
    simulation.add_server(
        data_center_id=0,
        gpu_capacity=2,
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=5,
    )
    simulation.add_job(
        user_id=0,
        arrival_time=0,
        deadline=10,
        duration=2,
        gpu_required=1,
        priority=3,
        region="us-east",
    )

    simulation.step()

    job = simulation.jobs[0]
    assert job.status == "RUNNING"
    assert job.assigned_server == 0
    assert simulation.servers[0].available_gpus == 1


def test_live_simulation_completes_running_job_after_duration():
    simulation = LiveSimulation()
    simulation.add_data_center("us-east", energy_cost=1.0, base_latency=5)
    simulation.add_server(
        data_center_id=0,
        gpu_capacity=1,
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=5,
    )
    simulation.add_job(
        user_id=0,
        arrival_time=0,
        deadline=10,
        duration=1,
        gpu_required=1,
        priority=3,
        region="us-east",
    )

    simulation.run_ticks(2)

    assert simulation.jobs[0].status == "COMPLETED"
    assert simulation.jobs[0].finish_time == 1
    assert simulation.servers[0].available_gpus == 1


def test_live_simulation_rejects_expired_waiting_job():
    simulation = LiveSimulation()
    simulation.add_job(
        user_id=0,
        arrival_time=0,
        deadline=0,
        duration=1,
        gpu_required=1,
        priority=3,
        region="us-east",
    )

    simulation.run_ticks(2)

    assert simulation.jobs[0].status == "REJECTED"


def test_live_simulation_schedules_job_added_after_clock_advances():
    simulation = LiveSimulation()
    simulation.add_data_center("us-east", energy_cost=1.0, base_latency=5)
    simulation.add_server(
        data_center_id=0,
        gpu_capacity=1,
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=5,
    )
    simulation.run_ticks(3)
    simulation.add_job(
        user_id=0,
        arrival_time=simulation.current_time,
        deadline=10,
        duration=2,
        gpu_required=1,
        priority=3,
        region="us-east",
    )

    simulation.step()

    assert simulation.jobs[0].status == "RUNNING"
    assert simulation.jobs[0].start_time == 3


def test_live_simulation_loads_dry_run_template():
    simulation = LiveSimulation()

    simulation.load_dry_run_template()

    assert simulation.current_time == 0
    assert len(simulation.data_centers) == 2
    assert len(simulation.servers) == 2
    assert len(simulation.jobs) == 3
    assert [job.duration for job in simulation.jobs] == [3, 2, 2]
