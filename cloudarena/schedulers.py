import heapq
from typing import Iterable

from cloudarena.min_cost_flow import MinCostFlow
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


class FlowScheduler(Scheduler):
    name = "flow"
    deadline_penalty_per_tick = 20
    region_mismatch_penalty = 25
    priority_base = 10

    def schedule(
        self,
        jobs: list[Job],
        servers: list[Server],
        current_time: int,
    ) -> list[Assignment]:
        waiting_jobs = sorted(jobs, key=lambda job: job.job_id)
        available_servers = sorted(
            [server for server in servers if server.available_gpus > 0],
            key=lambda server: server.server_id,
        )

        if not waiting_jobs or not available_servers:
            return []

        source = 0
        first_job_node = 1
        first_server_node = first_job_node + len(waiting_jobs)
        sink = first_server_node + len(available_servers)

        flow = MinCostFlow(sink + 1)
        edge_records: list[tuple[Job, Server, int, int]] = []

        for job_index, job in enumerate(waiting_jobs):
            job_node = first_job_node + job_index
            flow.add_edge(source, job_node, capacity=1, cost=0)

        for server_index, server in enumerate(available_servers):
            server_node = first_server_node + server_index
            flow.add_edge(server_node, sink, capacity=server.available_gpus, cost=0)

        for job_index, job in enumerate(waiting_jobs):
            job_node = first_job_node + job_index

            for server_index, server in enumerate(available_servers):
                if server.available_gpus < job.gpu_required:
                    continue

                server_node = first_server_node + server_index
                edge_index = len(flow.graph[job_node])
                flow.add_edge(
                    job_node,
                    server_node,
                    capacity=1,
                    cost=self.compute_cost(job, server, current_time),
                )
                edge_records.append((job, server, job_node, edge_index))

        if not edge_records:
            return []

        max_assignments = min(
            len(waiting_jobs),
            sum(server.available_gpus for server in available_servers),
        )
        flow.min_cost_flow(source, sink, max_assignments)

        return self._extract_assignments(flow, edge_records)

    @classmethod
    def compute_cost(cls, job: Job, server: Server, current_time: int) -> float:
        server_cost = server.cost_per_tick * job.duration_mean
        latency_cost = server.latency
        deadline_penalty = (
            max(0, current_time + job.duration_mean - job.deadline)
            * cls.deadline_penalty_per_tick
        )
        failure_penalty = server.failure_probability * job.private_value
        region_penalty = (
            0
            if server.region == job.region
            else cls.region_mismatch_penalty
        )
        priority_cost = max(0, cls.priority_base - job.priority)

        return round(
            server_cost
            + latency_cost
            + deadline_penalty
            + failure_penalty
            + region_penalty
            + priority_cost,
            2,
        )

    @staticmethod
    def _extract_assignments(
        flow: MinCostFlow,
        edge_records: list[tuple[Job, Server, int, int]],
    ) -> list[Assignment]:
        assignments: list[Assignment] = []
        assigned_jobs: set[int] = set()
        remaining_gpus = {
            server.server_id: server.available_gpus
            for _, server, _, _ in edge_records
        }

        for job, server, job_node, edge_index in sorted(
            edge_records,
            key=lambda record: (record[0].job_id, record[1].server_id),
        ):
            edge = flow.graph[job_node][edge_index]
            if edge.capacity != 0:
                continue
            if job.job_id in assigned_jobs:
                continue
            if remaining_gpus[server.server_id] < job.gpu_required:
                continue

            assignments.append((job.job_id, server.server_id))
            assigned_jobs.add(job.job_id)
            remaining_gpus[server.server_id] -= job.gpu_required

        return assignments


def create_scheduler(name: str) -> Scheduler:
    schedulers = {
        "fcfs": FCFSScheduler,
        "edf": EarliestDeadlineFirstScheduler,
        "flow": FlowScheduler,
        "priority": PriorityScheduler,
    }

    try:
        return schedulers[name]()
    except KeyError as exc:
        valid = ", ".join(sorted(schedulers))
        raise ValueError(f"Unknown scheduler '{name}'. Valid options: {valid}") from exc
