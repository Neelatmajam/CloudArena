from cloudarena.models import SimulationConfig
from cloudarena.workload import generate_workload


config = SimulationConfig(seed=42)

jobs, servers, agents, data_centers = generate_workload(config, config.seed)

print(f"Generated {len(jobs)} jobs")
print(f"Generated {len(servers)} servers")
print(f"Generated {len(agents)} users")
print(f"Generated {len(data_centers)} data centers")