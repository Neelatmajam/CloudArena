import random

from cloudarena.probability import (
    sample_arrival_time,
    sample_runtime,
    should_fail,
)


def test_sample_runtime_can_be_disabled():
    rng = random.Random(1)

    assert sample_runtime(5, 2, rng, runtime_uncertainty=False) == 5


def test_sample_runtime_is_positive_when_uncertain():
    rng = random.Random(1)

    samples = [
        sample_runtime(2, 10, rng, runtime_uncertainty=True)
        for _ in range(25)
    ]

    assert all(sample >= 1 for sample in samples)


def test_should_fail_handles_boundary_probabilities():
    rng = random.Random(1)

    assert should_fail(0.0, rng) is False
    assert should_fail(1.0, rng) is True


def test_sample_arrival_time_stays_inside_horizon():
    rng = random.Random(7)

    arrivals = [sample_arrival_time(100, rng) for _ in range(100)]

    assert all(0 <= arrival <= 100 for arrival in arrivals)
    assert any(arrival > 50 for arrival in arrivals)
