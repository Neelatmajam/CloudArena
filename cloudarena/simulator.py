import random

from cloudarena.metrics import Metrics
from cloudarena.models import Job, Server, SimulationConfig
from cloudarena.probability import sample_runtime, should_fail
from cloudarena.schedulers import Scheduler


TERMINAL_STATUSES = {"COMPLETED", "FAILED", "REJECTED"}
TIMELINE_NAMES = ("waiting", "running", "completed", "failed", "rejected")


class Simulator:
    def __init__(
        self,
        jobs: list[Job],
        servers: list[Server],
        scheduler: Scheduler,
        config: SimulationConfig,
        seed: int | None = None,
    ):
        self.jobs = jobs
        self.servers = servers
        self.scheduler = scheduler
        self.config = config
        self.rng = random.Random(seed if seed is not None else config.seed)

        self.jobs_by_id = {job.job_id: job for job in jobs}
        self.servers_by_id = {server.server_id: server for server in servers}

        self.gpu_usage_ticks = 0
        self.gpu_capacity_ticks = 0
        self.total_cost = 0.0
        self.timelines = {name: [] for name in TIMELINE_NAMES}

    def run(self) -> Metrics:
        last_time = -1

        for current_time in range(self._end_time() + 1):
            last_time = current_time
            self._update_running_jobs(current_time)
            self._reject_expired_waiting_jobs(current_time)
            self._schedule_waiting_jobs(current_time)
            self._record_gpu_usage()
            self._record_timelines(current_time)

            if self._all_jobs_terminal():
                break

        if self._close_unfinished_jobs():
            self._record_timelines(last_time + 1)

        return Metrics.from_simulation(
            self.jobs,
            self.gpu_usage_ticks,
            self.gpu_capacity_ticks,
            self.total_cost,
        )

    def _end_time(self) -> int:
        if not self.jobs:
            return self.config.time_horizon

        latest_deadline = max(job.deadline for job in self.jobs)
        longest_duration = max(
            job.duration_mean + (3 * job.duration_std)
            for job in self.jobs
        )
        return max(self.config.time_horizon, latest_deadline + longest_duration + 1)

    def _update_running_jobs(self, current_time: int) -> None:
        for server in self.servers:
            for job_id in list(server.running_jobs):
                job = self.jobs_by_id[job_id]

                if self._job_has_finished(job, current_time):
                    self._complete_job(job, server, current_time)
                    continue

                if should_fail(server.failure_probability, self.rng):
                    self._fail_job(job, server, current_time)

    @staticmethod
    def _job_has_finished(job: Job, current_time: int) -> bool:
        if job.start_time is None or job.actual_duration is None:
            return False
        return current_time >= job.start_time + job.actual_duration

    def _complete_job(self, job: Job, server: Server, current_time: int) -> None:
        job.status = "COMPLETED"
        job.finish_time = current_time
        self._release_job(job, server)

    def _fail_job(self, job: Job, server: Server, current_time: int) -> None:
        job.status = "FAILED"
        job.finish_time = current_time
        self._release_job(job, server)

    @staticmethod
    def _release_job(job: Job, server: Server) -> None:
        server.available_gpus += job.gpu_required
        if job.job_id in server.running_jobs:
            server.running_jobs.remove(job.job_id)

    def _reject_expired_waiting_jobs(self, current_time: int) -> None:
        for job in self.jobs:
            if (
                job.status == "WAITING"
                and job.arrival_time <= current_time
                and current_time > job.deadline
            ):
                job.status = "REJECTED"
                job.finish_time = current_time

    def _schedule_waiting_jobs(self, current_time: int) -> None:
        waiting_jobs = [
            job
            for job in self.jobs
            if job.status == "WAITING" and job.arrival_time <= current_time
        ]

        assignments = self.scheduler.schedule(waiting_jobs, self.servers, current_time)

        for job_id, server_id in assignments:
            job = self.jobs_by_id[job_id]
            server = self.servers_by_id[server_id]

            if job.status != "WAITING" or job.arrival_time > current_time:
                continue
            if current_time > job.deadline:
                continue
            if server.available_gpus < job.gpu_required:
                continue

            self._start_job(job, server, current_time)

    def _start_job(self, job: Job, server: Server, current_time: int) -> None:
        job.status = "RUNNING"
        job.start_time = current_time
        job.actual_duration = sample_runtime(
            job.duration_mean,
            job.duration_std,
            self.rng,
            self.config.runtime_uncertainty,
        )
        job.assigned_server = server.server_id

        server.available_gpus -= job.gpu_required
        server.running_jobs.append(job.job_id)

    def _record_gpu_usage(self) -> None:
        total_capacity = sum(server.gpu_capacity for server in self.servers)
        used_gpus = sum(
            server.gpu_capacity - server.available_gpus
            for server in self.servers
        )

        self.gpu_usage_ticks += used_gpus
        self.gpu_capacity_ticks += total_capacity
        self.total_cost += sum(
            (server.gpu_capacity - server.available_gpus) * server.cost_per_tick
            for server in self.servers
        )

    def _record_timelines(self, current_time: int) -> None:
        buckets = {name: [] for name in TIMELINE_NAMES}

        for job in self.jobs:
            if job.status == "WAITING":
                if job.arrival_time <= current_time:
                    buckets["waiting"].append(job.job_id)
            elif job.status == "RUNNING":
                buckets["running"].append(job.job_id)
            elif job.status == "COMPLETED":
                buckets["completed"].append(job.job_id)
            elif job.status == "FAILED":
                buckets["failed"].append(job.job_id)
            elif job.status == "REJECTED":
                buckets["rejected"].append(job.job_id)

        for name, job_ids in buckets.items():
            self.timelines[name].append(
                {
                    "time": current_time,
                    "job_ids": sorted(job_ids),
                }
            )

    def _all_jobs_terminal(self) -> bool:
        return all(job.status in TERMINAL_STATUSES for job in self.jobs)

    def _close_unfinished_jobs(self) -> bool:
        changed = False

        for job in self.jobs:
            if job.status == "WAITING":
                job.status = "REJECTED"
                changed = True
            elif job.status == "RUNNING" and job.assigned_server is not None:
                server = self.servers_by_id[job.assigned_server]
                job.status = "FAILED"
                self._release_job(job, server)
                changed = True

        return changed
