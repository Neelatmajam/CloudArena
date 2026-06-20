import random

from cloudarena.models import Agent, DataCenter, Job, Server, SimulationConfig
from cloudarena.probability import sample_arrival_time
from cloudarena.config import GPU_CAPACITY_OPTIONS, GPU_REQUIRED_OPTIONS, REGIONS


def generate_workload(config: SimulationConfig, seed: int | None = None):
    rng = random.Random(seed if seed is not None else config.seed)

    agents = generate_agents(config, rng)
    data_centers = generate_data_centers(config, rng)
    servers = generate_servers(config, data_centers, rng)
    jobs = generate_jobs(config, agents, rng)

    return jobs, servers, agents, data_centers


def generate_agents(config: SimulationConfig, rng: random.Random):
    agents = []

    for agent_id in range(config.num_agents):
        agents.append(Agent(agent_id=agent_id))

    return agents


def generate_data_centers(config: SimulationConfig, rng: random.Random):
    data_centers = []

    for data_center_id in range(config.num_data_centers):
        region = REGIONS[data_center_id % len(REGIONS)]

        data_center = DataCenter(
            data_center_id=data_center_id,
            region=region,
            servers=[],
            energy_cost=round(rng.uniform(0.5, 2.0), 2),
            base_latency=rng.randint(5, 40),
        )
        data_centers.append(data_center)

    return data_centers


def generate_servers(config: SimulationConfig, data_centers, rng: random.Random):
    servers = []

    for server_id in range(config.num_servers):
        data_center = data_centers[server_id % len(data_centers)]

        gpu_capacity = rng.choice(GPU_CAPACITY_OPTIONS)

        server = Server(
            server_id=server_id,
            data_center_id=data_center.data_center_id,
            region=data_center.region,
            gpu_capacity=gpu_capacity,
            available_gpus=gpu_capacity,
            cost_per_tick=round(rng.uniform(1.0, 5.0), 2),
            failure_probability=config.default_failure_probability,
            latency=data_center.base_latency + rng.randint(0, 20),
        )

        servers.append(server)
        data_center.servers.append(server)

    return servers


def generate_jobs(config: SimulationConfig, agents, rng: random.Random):
    jobs = []

    for job_id in range(config.num_jobs):
        agent = rng.choice(agents)

        arrival_time = sample_arrival_time(config.time_horizon, rng)
        duration = rng.randint(2, 12)
        deadline = arrival_time + duration + rng.randint(5, 25)

        job = Job(
            job_id=job_id,
            user_id=agent.agent_id,
            arrival_time=arrival_time,
            deadline=deadline,
            duration=duration,
            gpu_required=rng.choice(GPU_REQUIRED_OPTIONS),
            priority=rng.randint(1, 5),
            region=rng.choice(REGIONS),
        )

        jobs.append(job)

    return jobs
