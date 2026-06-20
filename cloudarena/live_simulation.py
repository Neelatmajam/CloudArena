import random
from dataclasses import dataclass, field

from cloudarena.config import REGIONS
from cloudarena.models import DataCenter, Job, Server
from cloudarena.probability import should_fail
from cloudarena.schedulers import create_scheduler


JOB_STATUSES = ("WAITING", "RUNNING", "COMPLETED", "FAILED", "REJECTED")


@dataclass
class LiveSimulation:
    scheduler_name: str = "flow"
    seed: int = 42
    current_time: int = 0
    regions: list[str] = field(default_factory=lambda: list(REGIONS))
    data_centers: list[DataCenter] = field(default_factory=list)
    servers: list[Server] = field(default_factory=list)
    jobs: list[Job] = field(default_factory=list)
    history: list[dict[str, int | float]] = field(default_factory=list)
    rng: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)

    def add_region(self, region: str) -> bool:
        normalized = region.strip()
        if not normalized or normalized in self.regions:
            return False

        self.regions.append(normalized)
        return True

    def add_data_center(
        self,
        region: str,
        energy_cost: float,
        base_latency: int,
    ) -> DataCenter:
        data_center = DataCenter(
            data_center_id=len(self.data_centers),
            region=region,
            servers=[],
            energy_cost=energy_cost,
            base_latency=base_latency,
        )
        self.data_centers.append(data_center)
        return data_center

    def add_server(
        self,
        data_center_id: int,
        gpu_capacity: int,
        cost_per_tick: float,
        failure_probability: float,
        latency: int,
    ) -> Server:
        data_center = self.data_centers[data_center_id]
        server = Server(
            server_id=len(self.servers),
            data_center_id=data_center.data_center_id,
            region=data_center.region,
            gpu_capacity=gpu_capacity,
            available_gpus=gpu_capacity,
            cost_per_tick=cost_per_tick,
            failure_probability=failure_probability,
            latency=latency,
        )
        self.servers.append(server)
        data_center.servers.append(server)
        return server

    def add_job(
        self,
        user_id: int,
        arrival_time: int,
        deadline: int,
        duration: int,
        gpu_required: int,
        priority: int,
        region: str,
    ) -> Job:
        job = Job(
            job_id=len(self.jobs),
            user_id=user_id,
            arrival_time=arrival_time,
            deadline=deadline,
            duration=duration,
            gpu_required=gpu_required,
            priority=priority,
            region=region,
        )
        self.jobs.append(job)
        return job

    def load_dry_run_template(self) -> None:
        self.current_time = 0
        self.regions = ["us-east", "europe"]
        self.data_centers = []
        self.servers = []
        self.jobs = []
        self.history = []

        east_dc = self.add_data_center("us-east", energy_cost=1.0, base_latency=5)
        europe_dc = self.add_data_center("europe", energy_cost=1.4, base_latency=8)
        self.add_server(
            data_center_id=east_dc.data_center_id,
            gpu_capacity=2,
            cost_per_tick=1.0,
            failure_probability=0.0,
            latency=5,
        )
        self.add_server(
            data_center_id=europe_dc.data_center_id,
            gpu_capacity=2,
            cost_per_tick=1.3,
            failure_probability=0.0,
            latency=8,
        )
        self.add_job(
            user_id=0,
            arrival_time=0,
            deadline=5,
            duration=3,
            gpu_required=1,
            priority=5,
            region="us-east",
        )
        self.add_job(
            user_id=1,
            arrival_time=0,
            deadline=4,
            duration=2,
            gpu_required=1,
            priority=3,
            region="europe",
        )
        self.add_job(
            user_id=2,
            arrival_time=1,
            deadline=7,
            duration=2,
            gpu_required=2,
            priority=4,
            region="us-east",
        )

    def step(self) -> None:
        self._update_running_jobs()
        self._reject_expired_waiting_jobs()
        self._schedule_waiting_jobs()
        self._record_snapshot()
        self.current_time += 1

    def run_ticks(self, ticks: int) -> None:
        for _ in range(max(0, ticks)):
            self.step()

    def status_counts(self) -> dict[str, int]:
        return {
            status.lower(): sum(job.status == status for job in self.jobs)
            for status in JOB_STATUSES
        }

    def server_rows(self) -> list[dict[str, int | float | str]]:
        rows = []
        for server in self.servers:
            used_gpus = server.gpu_capacity - server.available_gpus
            rows.append(
                {
                    "server_id": server.server_id,
                    "data_center_id": server.data_center_id,
                    "region": server.region,
                    "gpu_capacity": server.gpu_capacity,
                    "used_gpus": used_gpus,
                    "available_gpus": server.available_gpus,
                    "running_jobs": list(server.running_jobs),
                    "cost_per_tick": server.cost_per_tick,
                    "failure_probability": server.failure_probability,
                    "latency": server.latency,
                }
            )
        return rows

    def job_rows(
        self,
        statuses: set[str] | None = None,
    ) -> list[dict[str, int | float | str | None]]:
        rows = []
        for job in self.jobs:
            if statuses is not None and job.status not in statuses:
                continue

            rows.append(
                {
                    "job_id": job.job_id,
                    "status": job.status,
                    "user_id": job.user_id,
                    "region": job.region,
                    "arrival_time": job.arrival_time,
                    "deadline": job.deadline,
                    "duration": job.duration,
                    "actual_duration": job.actual_duration,
                    "gpu_required": job.gpu_required,
                    "priority": job.priority,
                    "assigned_server": job.assigned_server,
                    "start_time": job.start_time,
                    "finish_time": job.finish_time,
                }
            )
        return rows

    def data_center_rows(self) -> list[dict[str, int | float | str]]:
        return [
            {
                "data_center_id": data_center.data_center_id,
                "region": data_center.region,
                "servers": len(data_center.servers),
                "energy_cost": data_center.energy_cost,
                "base_latency": data_center.base_latency,
            }
            for data_center in self.data_centers
        ]

    def _update_running_jobs(self) -> None:
        jobs_by_id = {job.job_id: job for job in self.jobs}

        for server in self.servers:
            for job_id in list(server.running_jobs):
                job = jobs_by_id[job_id]

                if self._job_has_finished(job):
                    job.status = "COMPLETED"
                    job.finish_time = self.current_time
                    self._release_job(job, server)
                    continue

                if should_fail(server.failure_probability, self.rng):
                    job.status = "FAILED"
                    job.finish_time = self.current_time
                    self._release_job(job, server)

    def _reject_expired_waiting_jobs(self) -> None:
        for job in self.jobs:
            if (
                job.status == "WAITING"
                and job.arrival_time <= self.current_time
                and self.current_time > job.deadline
            ):
                job.status = "REJECTED"
                job.finish_time = self.current_time

    def _schedule_waiting_jobs(self) -> None:
        if not self.servers:
            return

        waiting_jobs = [
            job
            for job in self.jobs
            if job.status == "WAITING" and job.arrival_time <= self.current_time
        ]
        assignments = create_scheduler(self.scheduler_name).schedule(
            waiting_jobs,
            self.servers,
            self.current_time,
        )
        jobs_by_id = {job.job_id: job for job in self.jobs}
        servers_by_id = {server.server_id: server for server in self.servers}

        for job_id, server_id in assignments:
            job = jobs_by_id[job_id]
            server = servers_by_id[server_id]

            if job.status != "WAITING" or self.current_time > job.deadline:
                continue
            if server.available_gpus < job.gpu_required:
                continue

            job.status = "RUNNING"
            job.start_time = self.current_time
            job.actual_duration = max(1, job.duration)
            job.assigned_server = server.server_id
            server.available_gpus -= job.gpu_required
            server.running_jobs.append(job.job_id)

    def _record_snapshot(self) -> None:
        counts = self.status_counts()
        total_capacity = sum(server.gpu_capacity for server in self.servers)
        used_gpus = sum(
            server.gpu_capacity - server.available_gpus
            for server in self.servers
        )

        self.history.append(
            {
                "time": self.current_time,
                "waiting": counts["waiting"],
                "running": counts["running"],
                "completed": counts["completed"],
                "failed": counts["failed"],
                "rejected": counts["rejected"],
                "used_gpus": used_gpus,
                "total_gpus": total_capacity,
            }
        )

    def _job_has_finished(self, job: Job) -> bool:
        if job.start_time is None or job.actual_duration is None:
            return False
        return self.current_time >= job.start_time + job.actual_duration

    @staticmethod
    def _release_job(job: Job, server: Server) -> None:
        server.available_gpus += job.gpu_required
        if job.job_id in server.running_jobs:
            server.running_jobs.remove(job.job_id)
