from __future__ import annotations

import csv
import time
from dataclasses import asdict
from io import StringIO
from typing import Iterable

try:
    import matplotlib.pyplot as plt
    import streamlit as st
except ModuleNotFoundError as exc:
    missing = exc.name
    raise SystemExit(
        f"Missing dependency '{missing}'. Install dependencies with: "
        "python3 -m pip install -r requirements.txt"
    ) from exc

from cloudarena.live_simulation import LiveSimulation
from cloudarena.monte_carlo import (
    MONTE_CARLO_SCHEDULERS,
    MonteCarloRun,
    run_monte_carlo,
    summarize_results,
)
from cloudarena.models import SimulationConfig


SCHEDULER_LABELS = {
    "fcfs": "FCFS",
    "edf": "Earliest Deadline First",
    "priority": "Priority",
    "flow": "Min-Cost Flow",
}
LIVE_SCHEDULERS = tuple(SCHEDULER_LABELS)


def main() -> None:
    st.set_page_config(page_title="CloudArena", layout="wide")
    st.title("CloudArena")

    live_tab, monte_carlo_tab = st.tabs(["Live Simulator", "Monte Carlo Summary"])

    with live_tab:
        render_live_simulator()

    with monte_carlo_tab:
        render_monte_carlo_dashboard()


def render_live_simulator() -> None:
    simulation = ensure_live_simulation()

    render_clock_controls(simulation)

    builder_column, job_column = st.columns(2)
    with builder_column:
        render_world_builder(simulation)
    with job_column:
        render_job_builder(simulation)

    render_live_state(simulation)

    if st.session_state.get("live_playing", False):
        simulation.step()
        time.sleep(st.session_state.get("tick_delay_seconds", 0.7))
        st.rerun()


def ensure_live_simulation() -> LiveSimulation:
    if "live_simulation" not in st.session_state:
        st.session_state.live_simulation = LiveSimulation()
    if "live_playing" not in st.session_state:
        st.session_state.live_playing = False
    if "tick_delay_seconds" not in st.session_state:
        st.session_state.tick_delay_seconds = 0.7

    return st.session_state.live_simulation


def reset_live_simulation(
    scheduler_name: str,
    seed: int,
) -> None:
    st.session_state.live_simulation = LiveSimulation(
        scheduler_name=scheduler_name,
        seed=seed,
    )
    st.session_state.live_playing = False


def render_clock_controls(simulation: LiveSimulation) -> None:
    st.subheader("Live Simulation")

    counts = simulation.status_counts()
    metric_columns = st.columns(6)
    metric_columns[0].metric("Time", simulation.current_time)
    metric_columns[1].metric("Waiting", counts["waiting"])
    metric_columns[2].metric("Running", counts["running"])
    metric_columns[3].metric("Completed", counts["completed"])
    metric_columns[4].metric("Failed", counts["failed"])
    metric_columns[5].metric("Rejected", counts["rejected"])

    settings = st.columns([2, 1.2, 1.2])
    with settings[0]:
        scheduler_name = st.selectbox(
            "Scheduler",
            options=LIVE_SCHEDULERS,
            format_func=lambda name: SCHEDULER_LABELS[name],
            index=scheduler_index(simulation.scheduler_name),
            key="live_scheduler",
        )
    with settings[1]:
        seed = st.number_input(
            "Seed",
            min_value=0,
            max_value=1_000_000,
            value=simulation.seed,
            key="live_seed",
        )
    with settings[2]:
        st.session_state.tick_delay_seconds = st.slider(
            "Tick delay",
            min_value=0.1,
            max_value=2.0,
            value=float(st.session_state.tick_delay_seconds),
            step=0.1,
            key="live_tick_delay",
        )

    simulation.scheduler_name = scheduler_name
    if simulation.seed != int(seed):
        simulation.seed = int(seed)
        simulation.rng.seed(simulation.seed)

    controls = st.columns(6)
    with controls[0]:
        if st.button(
            "Start",
            disabled=st.session_state.live_playing,
            icon=":material/play_arrow:",
            width="stretch",
        ):
            st.session_state.live_playing = True
            st.rerun()
    with controls[1]:
        if st.button(
            "Pause",
            disabled=not st.session_state.live_playing,
            icon=":material/pause:",
            width="stretch",
        ):
            st.session_state.live_playing = False
    with controls[2]:
        if st.button(
            "Step",
            disabled=st.session_state.live_playing,
            icon=":material/skip_next:",
            width="stretch",
        ):
            simulation.step()
            st.rerun()
    with controls[3]:
        if st.button(
            "Run 5",
            disabled=st.session_state.live_playing,
            icon=":material/fast_forward:",
            width="stretch",
        ):
            simulation.run_ticks(5)
            st.rerun()
    with controls[4]:
        if st.button("Reset", icon=":material/restart_alt:", width="stretch"):
            reset_live_simulation(scheduler_name, int(seed))
            st.rerun()
    with controls[5]:
        if st.button(
            "Dry Run",
            icon=":material/content_paste:",
            width="stretch",
        ):
            simulation.load_dry_run_template()
            st.session_state.live_playing = False
            st.rerun()


def scheduler_index(name: str) -> int:
    if name in LIVE_SCHEDULERS:
        return LIVE_SCHEDULERS.index(name)
    return LIVE_SCHEDULERS.index("flow")


def render_world_builder(simulation: LiveSimulation) -> None:
    st.subheader("Topology Builder")

    region_tab, data_center_tab, server_tab = st.tabs(
        ["Regions", "Data Centers", "Servers"]
    )

    with region_tab:
        with st.form("add-region-form", clear_on_submit=True):
            region_name = st.text_input("Region name", placeholder="ap-south")
            submitted = st.form_submit_button(
                "Add Region",
                icon=":material/add:",
                width="stretch",
            )
            if submitted:
                if simulation.add_region(region_name):
                    st.success("Region added.")
                    st.rerun()
                else:
                    st.warning("Region already exists or is empty.")

        render_rows(
            "Current Regions",
            [{"region": region} for region in simulation.regions],
            "No regions available.",
        )

    with data_center_tab:
        with st.form("add-data-center-form"):
            region = st.selectbox("Region", options=simulation.regions)
            energy_cost = st.number_input(
                "Energy cost",
                min_value=0.0,
                max_value=1000.0,
                value=1.0,
                step=0.1,
            )
            base_latency = st.number_input(
                "Base latency",
                min_value=0,
                max_value=1000,
                value=5,
            )
            submitted = st.form_submit_button(
                "Add Data Center",
                icon=":material/add:",
                width="stretch",
            )
            if submitted:
                simulation.add_data_center(
                    region,
                    float(energy_cost),
                    int(base_latency),
                )
                st.success("Data center added.")
                st.rerun()

        render_rows(
            "Data Centers",
            simulation.data_center_rows(),
            "No data centers created.",
        )

    with server_tab:
        if simulation.data_centers:
            data_center_options = {
                (
                    f"DC {data_center.data_center_id} | "
                    f"{data_center.region}"
                ): data_center.data_center_id
                for data_center in simulation.data_centers
            }
            with st.form("add-server-form"):
                selected_data_center = st.selectbox(
                    "Data center",
                    options=list(data_center_options),
                )
                gpu_capacity = st.number_input(
                    "GPU capacity",
                    min_value=1,
                    max_value=128,
                    value=4,
                )
                cost_per_tick = st.number_input(
                    "Cost per tick",
                    min_value=0.0,
                    max_value=10_000.0,
                    value=1.0,
                    step=0.1,
                )
                failure_probability = st.slider(
                    "Failure probability",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.02,
                    step=0.01,
                )
                latency = st.number_input(
                    "Latency",
                    min_value=0,
                    max_value=1000,
                    value=5,
                )
                submitted = st.form_submit_button(
                    "Add Server",
                    icon=":material/add:",
                    width="stretch",
                )
                if submitted:
                    simulation.add_server(
                        data_center_options[selected_data_center],
                        int(gpu_capacity),
                        float(cost_per_tick),
                        float(failure_probability),
                        int(latency),
                    )
                    st.success("Server added.")
                    st.rerun()
        else:
            st.info("Create a data center before adding servers.")

        render_server_loads(simulation)


def render_job_builder(simulation: LiveSimulation) -> None:
    st.subheader("Job Builder")

    with st.form("add-job-form"):
        first_row = st.columns(3)
        with first_row[0]:
            user_id = st.number_input(
                "User ID",
                min_value=0,
                max_value=10_000,
                value=0,
            )
        with first_row[1]:
            region = st.selectbox("Job region", options=simulation.regions)
        with first_row[2]:
            priority = st.number_input(
                "Priority",
                min_value=1,
                max_value=10,
                value=5,
            )

        second_row = st.columns(3)
        with second_row[0]:
            arrival_time = st.number_input(
                "Arrival time",
                min_value=0,
                max_value=1_000_000,
                value=simulation.current_time,
            )
        with second_row[1]:
            deadline = st.number_input(
                "Deadline",
                min_value=0,
                max_value=1_000_000,
                value=simulation.current_time + 10,
            )
        with second_row[2]:
            gpu_required = st.number_input(
                "GPUs required",
                min_value=1,
                max_value=128,
                value=1,
            )

        third_row = st.columns(1)
        with third_row[0]:
            duration = st.number_input(
                "Duration",
                min_value=1,
                max_value=10_000,
                value=3,
            )

        submitted = st.form_submit_button(
            "Add Job",
            icon=":material/add:",
            width="stretch",
        )
        if submitted:
            if int(deadline) < int(arrival_time):
                st.error("Deadline must be greater than or equal to arrival time.")
            else:
                simulation.add_job(
                    user_id=int(user_id),
                    arrival_time=int(arrival_time),
                    deadline=int(deadline),
                    duration=int(duration),
                    gpu_required=int(gpu_required),
                    priority=int(priority),
                    region=region,
                )
                st.success("Job added.")
                st.rerun()

    render_job_tables(simulation)


def render_live_state(simulation: LiveSimulation) -> None:
    st.subheader("Live State")

    topology_column, timeline_column = st.columns([1, 1])

    with topology_column:
        render_rows(
            "Data Centers",
            simulation.data_center_rows(),
            "No data centers created.",
        )
        render_rows(
            "Servers",
            simulation.server_rows(),
            "No servers created.",
        )

    with timeline_column:
        if simulation.history:
            st.line_chart(
                simulation.history,
                x="time",
                y=["waiting", "running", "completed", "failed", "rejected"],
            )
            st.line_chart(simulation.history, x="time", y=["used_gpus"])
        else:
            st.info("No timeline samples recorded.")


def render_job_tables(simulation: LiveSimulation) -> None:
    waiting_tab, running_tab, completed_tab, failed_tab, rejected_tab, all_tab = st.tabs(
        ["Waiting", "Running", "Completed", "Failed", "Rejected", "All"]
    )
    job_views = (
        (waiting_tab, "Waiting Jobs", {"WAITING"}),
        (running_tab, "Running Jobs", {"RUNNING"}),
        (completed_tab, "Completed Jobs", {"COMPLETED"}),
        (failed_tab, "Failed Jobs", {"FAILED"}),
        (rejected_tab, "Rejected Jobs", {"REJECTED"}),
        (all_tab, "All Jobs", None),
    )

    for tab, title, statuses in job_views:
        with tab:
            render_rows(
                title,
                simulation.job_rows(statuses),
                f"No {title.lower()}.",
            )


def render_server_loads(simulation: LiveSimulation) -> None:
    rows = simulation.server_rows()
    if not rows:
        st.info("No servers created.")
        return

    st.markdown("**Server Load**")
    for row in rows:
        capacity = row["gpu_capacity"]
        used = row["used_gpus"]
        load = 0.0 if capacity == 0 else used / capacity
        running_jobs = row["running_jobs"] or []
        st.progress(
            load,
            text=(
                f"Server {row['server_id']} | DC {row['data_center_id']} | "
                f"{used}/{capacity} GPUs | jobs {running_jobs}"
            ),
        )


def render_rows(title: str, rows: list[dict], empty_message: str) -> None:
    st.markdown(f"**{title}**")
    if rows:
        st.dataframe(rows, hide_index=True, width="stretch")
    else:
        st.info(empty_message)


def render_monte_carlo_dashboard() -> None:
    st.subheader("Monte Carlo Summary")

    config, selected_scheduler, runs, compare_all = render_monte_carlo_controls()
    scheduler_names = MONTE_CARLO_SCHEDULERS if compare_all else (selected_scheduler,)
    summaries, all_runs = run_dashboard_experiment(scheduler_names, runs, config)

    render_summary_table(summaries)
    render_charts(summaries)
    render_flow_explanation()
    render_download(all_runs)


def render_monte_carlo_controls() -> tuple[SimulationConfig, str, int, bool]:
    first_row = st.columns([2, 1, 1])
    with first_row[0]:
        selected_scheduler = st.selectbox(
            "Monte Carlo scheduler",
            options=list(MONTE_CARLO_SCHEDULERS),
            format_func=lambda name: SCHEDULER_LABELS[name],
            index=3,
            key="mc_scheduler",
        )
    with first_row[1]:
        compare_all = st.checkbox("Compare all", value=True, key="mc_compare_all")
    with first_row[2]:
        runs = st.number_input(
            "Monte Carlo runs",
            min_value=1,
            max_value=200,
            value=30,
            key="mc_runs",
        )

    second_row = st.columns(4)
    with second_row[0]:
        num_jobs = st.number_input(
            "Jobs",
            min_value=1,
            max_value=500,
            value=39,
            key="mc_jobs",
        )
    with second_row[1]:
        num_servers = st.number_input(
            "Servers",
            min_value=1,
            max_value=100,
            value=3,
            key="mc_servers",
        )
    with second_row[2]:
        num_agents = st.number_input(
            "Users",
            min_value=1,
            max_value=200,
            value=5,
            key="mc_users",
        )
    with second_row[3]:
        num_data_centers = st.number_input(
            "Data centers",
            min_value=1,
            max_value=100,
            value=10,
            key="mc_data_centers",
        )

    third_row = st.columns(3)
    with third_row[0]:
        time_horizon = st.number_input(
            "Time horizon",
            min_value=1,
            max_value=1000,
            value=100,
            key="mc_time_horizon",
        )
    with third_row[1]:
        seed = st.number_input(
            "Experiment seed",
            min_value=0,
            max_value=1_000_000,
            value=42,
            key="mc_seed",
        )
    with third_row[2]:
        failure_probability = st.slider(
            "Default failure probability",
            min_value=0.0,
            max_value=0.25,
            value=0.02,
            step=0.005,
            key="mc_failure_probability",
        )
    config = SimulationConfig(
        num_jobs=int(num_jobs),
        num_servers=int(num_servers),
        num_agents=int(num_agents),
        num_data_centers=int(num_data_centers),
        time_horizon=int(time_horizon),
        seed=int(seed),
        default_failure_probability=float(failure_probability),
    )

    return config, selected_scheduler, int(runs), compare_all


@st.cache_data(show_spinner=False)
def run_dashboard_experiment(
    scheduler_names: tuple[str, ...],
    runs: int,
    config: SimulationConfig,
):
    summaries = []
    all_runs = []

    for scheduler_name in scheduler_names:
        scheduler_runs = run_monte_carlo(scheduler_name, runs, config)
        summaries.append(summarize_results(scheduler_runs))
        all_runs.extend(scheduler_runs)

    return summaries, all_runs


def render_summary_table(summaries) -> None:
    st.subheader("Results Table")
    rows = [
        {
            "Scheduler": SCHEDULER_LABELS[summary.scheduler],
            "Runs": summary.runs,
            "Avg Completed": round(summary.average_completed_jobs, 2),
            "Avg Failed": round(summary.average_failed_jobs, 2),
            "Avg Rejected": round(summary.average_rejected_jobs, 2),
            "Avg Misses": round(summary.average_deadline_misses, 2),
            "Avg Wait": round(summary.average_wait_time, 2),
            "Avg Utilization": round(summary.average_gpu_utilization, 2),
            "Avg Cost": round(summary.average_total_cost, 2),
        }
        for summary in summaries
    ]
    st.dataframe(rows, hide_index=True, width="stretch")


def render_charts(summaries) -> None:
    st.subheader("Scheduler Comparison Charts")
    chart_specs = [
        ("Average Completed Jobs", "average_completed_jobs"),
        ("Average Deadline Misses", "average_deadline_misses"),
        ("Average GPU Utilization", "average_gpu_utilization"),
        ("Average Total Cost", "average_total_cost"),
    ]

    first_row = st.columns(2)
    second_row = st.columns(2)
    chart_slots = [*first_row, *second_row]

    for slot, (title, field_name) in zip(chart_slots, chart_specs):
        with slot:
            figure = build_bar_chart(summaries, title, field_name)
            st.pyplot(figure, clear_figure=True)


def build_bar_chart(summaries, title: str, field_name: str):
    labels = [SCHEDULER_LABELS[summary.scheduler] for summary in summaries]
    values = [getattr(summary, field_name) for summary in summaries]

    figure, axis = plt.subplots(figsize=(5.4, 3.2))
    axis.bar(labels, values, color="#2f6f73")
    axis.set_title(title)
    axis.tick_params(axis="x", rotation=20)
    axis.grid(axis="y", alpha=0.25)
    figure.tight_layout()
    return figure


def render_flow_explanation() -> None:
    st.subheader("Flow Scheduler Explanation")
    st.write(
        "The flow scheduler builds a graph at each scheduling tick: "
        "`source -> waiting jobs -> available servers -> sink`. "
        "It then runs min-cost max-flow using Dijkstra with Johnson-style "
        "potentials and extracts job-server edges whose flow was used."
    )


def render_download(runs: Iterable[MonteCarloRun]) -> None:
    st.subheader("Export")
    output = StringIO()
    writer = csv.DictWriter(output, fieldnames=list(MonteCarloRun.__annotations__))
    writer.writeheader()
    for run in runs:
        writer.writerow(asdict(run))

    st.download_button(
        "Download Monte Carlo CSV",
        data=output.getvalue(),
        file_name="cloudarena_monte_carlo.csv",
        mime="text/csv",
        icon=":material/download:",
    )


if __name__ == "__main__":
    main()
