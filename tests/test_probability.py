import random

from cloudarena.probability import (
    sample_arrival_time,
    should_fail,
)


def test_should_fail_handles_boundary_probabilities():
    rng = random.Random(1)

    assert should_fail(0.0, rng) is False
    assert should_fail(1.0, rng) is True


def test_sample_arrival_time_stays_inside_horizon():
    rng = random.Random(7)

    arrivals = [sample_arrival_time(100, rng) for _ in range(100)]

    assert all(0 <= arrival <= 100 for arrival in arrivals)
    assert any(arrival > 50 for arrival in arrivals)
