import random


def should_fail(failure_probability: float, rng: random.Random) -> bool:
    if failure_probability <= 0:
        return False
    if failure_probability >= 1:
        return True

    return rng.random() < failure_probability


def sample_arrival_time(time_horizon: int, rng: random.Random) -> int:
    if time_horizon <= 0:
        return 0

    half_horizon = max(1, time_horizon // 2)
    mode = rng.random()

    if mode < 0.65:
        return rng.randint(0, half_horizon)

    if mode < 0.9:
        peak_center = time_horizon * 0.35
        peak_width = max(1, time_horizon * 0.08)
        sampled = int(round(rng.gauss(peak_center, peak_width)))
        return min(time_horizon, max(0, sampled))

    return rng.randint(half_horizon, time_horizon)
