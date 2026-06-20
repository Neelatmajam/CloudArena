from pathlib import Path


def test_dashboard_app_exists():
    assert Path("app.py").exists()


def test_dashboard_exposes_live_simulator_surface():
    source = Path("app.py").read_text()

    assert "Live Simulator" in source
    assert "render_world_builder" in source
    assert "render_job_builder" in source
    assert "st.session_state.live_simulation" in source


def test_dashboard_uses_simplified_job_form():
    source = Path("app.py").read_text()

    assert '"Dry Run"' in source
    assert '"Duration"' in source
    assert "Private value" not in source
    assert "Budget" not in source
    assert "Duration std" not in source
    assert "Runtime uncertainty" not in source
