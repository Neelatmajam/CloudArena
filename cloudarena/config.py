REGIONS = ["us-east", "us-west", "europe", "asia"]

STRATEGIES = [
    "truthful",
    "underbid",
    "overbid",
    "random",
    "deadline_panic",
]

JOB_STATUSES = [
    "WAITING",
    "RUNNING",
    "COMPLETED",
    "FAILED",
    "REJECTED",
]

SCHEDULERS = [
    "fcfs",
    "edf",
    "priority",
    "flow",
    "auction",
]

GPU_CAPACITY_OPTIONS = [2, 4, 8]
GPU_REQUIRED_OPTIONS = [1, 1, 1, 2]

DEFAULT_NUM_JOBS = 39
DEFAULT_NUM_SERVERS = 3
DEFAULT_NUM_AGENTS = 5
DEFAULT_NUM_DATA_CENTERS = 10
DEFAULT_TIME_HORIZON = 100
DEFAULT_SEED = 42
DEFAULT_FAILURE_PROBABILITY = 0.02