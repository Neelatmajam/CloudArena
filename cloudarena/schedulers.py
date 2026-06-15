import heapq
from typing import Iterable
from cloudarena.models import Job, Server


Assignment = tuple[int, int]

class Scheduler:
    name = "base"

    def schedule(
        self,
        jobs: list[Job],
        servers: list[Server],
        current_time: int,
    ) -> list[Assignment]:
        raise NotImplementedError

    def _assign_in_order(
        self,
        ordered_jobs: Iterable[Job],
        servers: list[Server],
    ) -> list[Assignment]:
        assignments: list[Assignment] = []
        remaining_gpus = {
            server.server_id: server.available_gpus
            for server in servers
        }

        for job in ordered_jobs:
            server = self._find_server(job, servers, remaining_gpus)
            if server is None:
                continue

            assignments.append((job.job_id, server.server_id))
            remaining_gpus[server.server_id] -= job.gpu_required

        return assignments

    @staticmethod
    def _find_server(
        job: Job,
        servers: list[Server],
        remaining_gpus: dict[int, int],
    ) -> Server | None:
        candidates = [
            server
            for server in servers
            if remaining_gpus[server.server_id] >= job.gpu_required
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda server: (
                server.region != job.region,
                server.cost_per_tick,
                server.latency,
                server.server_id,
            ),
        )


class FCFSScheduler(Scheduler):
    name = "fcfs"

    def schedule(
        self,
        jobs: list[Job],
        servers: list[Server],
        current_time: int,
    ) -> list[Assignment]:
        ordered_jobs = sorted(jobs, key=lambda job: (job.arrival_time, job.job_id))
        return self._assign_in_order(ordered_jobs, servers)


class EarliestDeadlineFirstScheduler(Scheduler):
    name = "edf"

    def schedule(
        self,
        jobs: list[Job],
        servers: list[Server],
        current_time: int,
    ) -> list[Assignment]:
        heap = [
            (job.deadline, -job.priority, job.duration_mean, job.job_id, job)
            for job in jobs
        ]
        heapq.heapify(heap)

        ordered_jobs = []
        while heap:
            ordered_jobs.append(heapq.heappop(heap)[4])

        return self._assign_in_order(ordered_jobs, servers)


class PriorityScheduler(Scheduler):
    name = "priority"

    def schedule(
        self,
        jobs: list[Job],
        servers: list[Server],
        current_time: int,
    ) -> list[Assignment]:
        heap = [
            (-job.priority, job.deadline, job.duration_mean, job.job_id, job)
            for job in jobs
        ]
        heapq.heapify(heap)

        ordered_jobs = []
        while heap:
            ordered_jobs.append(heapq.heappop(heap)[4])

        return self._assign_in_order(ordered_jobs, servers)


def create_scheduler(name: str) -> Scheduler:
    schedulers = {
        "fcfs": FCFSScheduler,
        "edf": EarliestDeadlineFirstScheduler,
        "priority": PriorityScheduler,
    }

    try:
        return schedulers[name]()
    except KeyError as exc:
        valid = ", ".join(sorted(schedulers))
        raise ValueError(f"Unknown scheduler '{name}'. Valid options: {valid}") from exc
