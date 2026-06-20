import pytest

from cloudarena.models import SimulationConfig


def test_simulation_config_rejects_non_positive_counts():
    with pytest.raises(ValueError, match="num_jobs must be positive"):
        SimulationConfig(num_jobs=0)


def test_simulation_config_rejects_invalid_failure_probability():
    with pytest.raises(ValueError, match="default_failure_probability"):
        SimulationConfig(default_failure_probability=1.5)
