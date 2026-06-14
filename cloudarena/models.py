from dataclasses import dataclass, field
from typing import Optional, List
from cloudarena.config import (
    DEFAULT_NUM_JOBS,
    DEFAULT_NUM_SERVERS,
    DEFAULT_NUM_AGENTS,
    DEFAULT_NUM_DATA_CENTERS,
    DEFAULT_TIME_HORIZON,
    DEFAULT_SEED,
    DEFAULT_FAILURE_PROBABILITY,
)


@dataclass
class Job:
    job_id: int
    user_id: int
    arrival_time: int
    deadline: int
    duration_mean: int
    duration_std: int
    gpu_required: int
    budget: float
    private_value: float
    priority: int
    region: str

    status: str = "WAITING"
    start_time: Optional[int] = None
    finish_time: Optional[int] = None
    assigned_server: Optional[int] = None
    actual_duration: Optional[int] = None
    payment: float = 0.0
    utility: float = 0.0


@dataclass
class Server:
    server_id: int
    data_center_id: int
    region: str
    gpu_capacity: int
    available_gpus: int
    cost_per_tick: float
    failure_probability: float
    latency: int
    running_jobs: List[int] = field(default_factory=list)


@dataclass
class Agent:
    agent_id: int
    strategy: str
    budget: float
    private_value_multiplier: float


@dataclass
class DataCenter:
    data_center_id: int
    region: str
    servers: List[Server]
    energy_cost: float
    base_latency: int


@dataclass
class SimulationConfig:
    num_jobs: int = DEFAULT_NUM_JOBS
    num_servers: int = DEFAULT_NUM_SERVERS
    num_agents: int = DEFAULT_NUM_AGENTS
    num_data_centers: int = DEFAULT_NUM_DATA_CENTERS
    time_horizon: int = DEFAULT_TIME_HORIZON
    seed: int = DEFAULT_SEED
    default_failure_probability: float = DEFAULT_FAILURE_PROBABILITY
    runtime_uncertainty: bool = True