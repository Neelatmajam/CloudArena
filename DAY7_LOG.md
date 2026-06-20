# Day 7 Implementation and Cleanup Log

## Scope

Implement the Streamlit dashboard and clean the project structure while keeping
auction/game-theory work out of scope.

## Human Difficulty Log

1. Resolving roadmap conflict.
   - Difficulty a human would face: the roadmap asks for auction analysis, but
     the current product decision says to skip game theory.
   - Approach: keep the dashboard focused on FCFS, EDF, Priority, Flow,
     probability, and Monte Carlo.
   - Why this approach beats the alternative: adding a half-finished auction
     section would make the project harder to explain and easier to break.

2. Choosing dashboard dependencies.
   - Difficulty a human would face: deciding whether to use a heavy dashboard
     stack or keep the demo small.
   - Approach: use Streamlit plus Matplotlib only.
   - Why this approach beats the alternative: it avoids frontend build tooling
     while still giving interactive controls, tables, charts, and CSV download.

3. Preventing unsafe or messy dashboard input.
   - Difficulty a human would face: UI controls can create invalid simulations,
     such as zero servers or impossible failure probabilities.
   - Approach: cap dashboard inputs and add `SimulationConfig.__post_init__`
     validation.
   - Why this approach beats the alternative: failing at the model boundary is
     safer than debugging crashes deep inside workload generation.

4. Keeping generated clutter out of the project.
   - Difficulty a human would face: local macOS and Python generated files make
     git status noisy.
   - Approach: add `.DS_Store` to `.gitignore`; keep existing generated files
     out of the feature logic.
   - Why this approach beats the alternative: a clean status makes real source
     changes easier to review.

5. Avoiding unsupported scheduler exposure.
   - Difficulty a human would face: `auction` still appeared in project
     constants even though no auction scheduler exists.
   - Approach: remove `auction` from `SCHEDULERS`.
   - Why this approach beats the alternative: advertised options should match
     runnable code.

6. Making dashboard charts useful without overbuilding.
   - Difficulty a human would face: the roadmap asks for many sections, and it
     is easy to turn the dashboard into a decorative landing page.
   - Approach: show exactly the decision metrics: completed jobs, deadline
     misses, utilization, and cost.
   - Why this approach beats the alternative: the dashboard answers scheduler
     comparison questions directly.

7. Preserving reproducibility.
   - Difficulty a human would face: Monte Carlo randomness can make charts look
     inconsistent unless seed handling is explicit.
   - Approach: reuse `run_monte_carlo()` and `SimulationConfig(seed=...)`.
   - Why this approach beats the alternative: the dashboard and CLI now share the
     same experiment logic.

8. Handling missing local dependencies.
   - Difficulty a human would face: the code can be correct but `streamlit run`
     still fails if Streamlit and Matplotlib are not installed.
   - Approach: add both packages to `requirements.txt`, then install the declared
     dependencies before verification.
   - Why this approach beats the alternative: the repo documents the actual
     runtime requirements instead of relying on hidden local packages.

9. Verifying a real local app under sandbox restrictions.
   - Difficulty a human would face: the first server bind failed inside the
     sandbox, and direct HTTP checks were blocked by local network restrictions.
   - Approach: run Streamlit with the approved local-server path and verify with
     the in-app browser.
   - Why this approach beats the alternative: a source-only check would not prove
     the dashboard actually renders.

10. Fixing UI runtime warnings.
    - Difficulty a human would face: Streamlit emitted a deprecation warning for
      `use_container_width`.
    - Approach: update the table call to `width="stretch"`.
    - Why this approach beats the alternative: removing known deprecations keeps
      the dashboard safer against future Streamlit upgrades.

11. Capturing a screenshot artifact.
    - Difficulty a human would face: the browser process could capture the page
      but could not write directly into the workspace.
    - Approach: save the screenshot to `/tmp`, then copy it into
      `screenshots/dashboard.png`.
    - Why this approach beats the alternative: the README now references a real
      generated dashboard image instead of a placeholder.

12. Verification completed.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
    - Result: `29 passed`
    - Command: `streamlit run app.py`
    - Result: dashboard rendered with Project Overview, Results Table, Scheduler
      Comparison Charts, Flow Scheduler Explanation, and CSV download.

13. Reworked dashboard from static report to live simulator.
    - Difficulty a human would face: the batch simulator produces a complete run
      from generated workload data, but a live dashboard needs partial state
      that can survive every Streamlit rerun.
    - Approach: add `LiveSimulation` as a small stateful engine and store it in
      `st.session_state`.
    - Why this approach beats the alternative: forcing the old batch simulator
      into UI callbacks would mix generated experiments with user-created
      topology and jobs, making the control flow harder to reason about.

14. Added dynamic topology creation.
    - Difficulty a human would face: servers depend on data centers, data
      centers depend on regions, and invalid order of creation can crash a UI.
    - Approach: separate region, data center, and server builders; only show the
      server form after at least one data center exists.
    - Why this approach beats the alternative: dependency-aware forms prevent
      impossible inputs without adding complicated validation branches later.

15. Added live job submission.
    - Difficulty a human would face: jobs can arrive after the clock has already
      moved, so the simulator cannot assume a fixed workload created at time
      zero.
    - Approach: allow jobs to be appended at any time and schedule all waiting
      jobs whose `arrival_time <= current_time` on every tick.
    - Why this approach beats the alternative: appending jobs keeps the model
      close to a real cloud queue where users submit work continuously.

16. Added clock controls.
    - Difficulty a human would face: Streamlit reruns the script on each
      interaction, so a normal `while` loop can freeze the page or lose state.
    - Approach: use buttons for start, pause, single-step, run-five, and reset;
      when playing, advance one tick and call `st.rerun()`.
    - Why this approach beats the alternative: one-tick reruns keep the UI
      responsive and make the simulation state visible after every update.

17. Preserved Monte Carlo analysis as a second tab.
    - Difficulty a human would face: replacing the static dashboard entirely
      would discard useful Day 6 statistical evaluation.
    - Approach: make the live simulator the first tab and move the Monte Carlo
      comparison into the second tab.
    - Why this approach beats the alternative: the project now supports both
      live demonstration and repeated-run evidence without duplicating code.

18. Added dynamic dashboard tests.
    - Difficulty a human would face: UI behavior is hard to test fully without a
      browser, but the simulation engine can still be guarded with unit tests.
    - Approach: add tests for a job submitted after the clock advances and a
      source-level test that the app exposes the live simulator surface.
    - Why this approach beats the alternative: testing the engine directly
      catches the scheduling semantics that matter most while keeping browser
      verification separate.

19. Verification after dynamic dashboard revision.
    - Command: `PYTHONDONTWRITEBYTECODE=1 python3 -m pytest`
    - Result: `34 passed`

20. Fixed stale live metrics after state-changing actions.
    - Difficulty a human would face: Streamlit renders top to bottom, so a
      button that mutates state after metrics are drawn can leave the top row
      showing the previous tick.
    - Approach: call `st.rerun()` after start, step, run-five, and successful
      add actions.
    - Why this approach beats the alternative: moving every metric below every
      form would make the page harder to scan and would not solve all rerun
      ordering problems.

21. Browser verification after rerun fix.
    - Action: opened `http://localhost:8501`, reset the simulation, added one
      data center, added one server, added one job, then clicked `Step`.
    - Result: the rendered page showed `Time = 1`, `Waiting = 0`,
      `Running = 1`, and `Server 0 | DC 0 | 1/4 GPUs | jobs [0]`.
    - Screenshot artifact: `screenshots/dashboard.png`
