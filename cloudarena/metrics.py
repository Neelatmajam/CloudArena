from dataclasses import dataclass

from cloudarena.models import Job


@dataclass
class Metrics:
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    rejected_jobs: int
    deadline_misses: int
    average_wait_time: float
    average_completion_time: float
    gpu_utilization: float
    total_cost: float

    @classmethod
    def from_simulation(
        cls,
        jobs: list[Job],
        gpu_usage_ticks: int,
        gpu_capacity_ticks: int,
        total_cost: float,
    ) -> "Metrics":
        completed_jobs = [job for job in jobs if job.status == "COMPLETED"]
        failed_jobs = [job for job in jobs if job.status == "FAILED"]
        rejected_jobs = [job for job in jobs if job.status == "REJECTED"]

        started_jobs = [job for job in jobs if job.start_time is not None]
        wait_times = [
            job.start_time - job.arrival_time
            for job in started_jobs
            if job.start_time is not None
        ]
        completion_times = [
            job.finish_time - job.arrival_time
            for job in completed_jobs
            if job.finish_time is not None
        ]

        deadline_misses = sum(
            1
            for job in jobs
            if job.status == "REJECTED"
            or (job.finish_time is not None and job.finish_time > job.deadline)
        )

        gpu_utilization = 0.0
        if gpu_capacity_ticks > 0:
            gpu_utilization = (gpu_usage_ticks / gpu_capacity_ticks) * 100

        return cls(
            total_jobs=len(jobs),
            completed_jobs=len(completed_jobs),
            failed_jobs=len(failed_jobs),
            rejected_jobs=len(rejected_jobs),
            deadline_misses=deadline_misses,
            average_wait_time=_average(wait_times),
            average_completion_time=_average(completion_times),
            gpu_utilization=gpu_utilization,
            total_cost=round(total_cost, 2),
        )

    def summary_lines(self, scheduler_name: str) -> list[str]:
        return [
            f"Scheduler: {scheduler_name.upper()}",
            f"Completed jobs: {self.completed_jobs}/{self.total_jobs}",
            f"Failed jobs: {self.failed_jobs}",
            f"Rejected jobs: {self.rejected_jobs}",
            f"Deadline misses: {self.deadline_misses}",
            f"Average wait time: {self.average_wait_time:.2f}",
            f"Average completion time: {self.average_completion_time:.2f}",
            f"GPU utilization: {self.gpu_utilization:.1f}%",
            f"Total cost: {self.total_cost:.2f}",
        ]


def _average(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)
