import pytest

from cloudarena.models import Job, Server


@pytest.fixture
def job_factory():
    def make_job(
        job_id,
        arrival_time=0,
        deadline=10,
        duration_mean=3,
        priority=1,
        gpu_required=1,
        region="us-east",
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
            region=region,
        )

    return make_job


@pytest.fixture
def server_factory():
    def make_server(
        server_id=0,
        available_gpus=1,
        gpu_capacity=1,
        region="us-east",
        cost_per_tick=1.0,
        failure_probability=0.0,
        latency=10,
    ):
        return Server(
            server_id=server_id,
            data_center_id=0,
            region=region,
            gpu_capacity=gpu_capacity,
            available_gpus=available_gpus,
            cost_per_tick=cost_per_tick,
            failure_probability=failure_probability,
            latency=latency,
        )

    return make_server
