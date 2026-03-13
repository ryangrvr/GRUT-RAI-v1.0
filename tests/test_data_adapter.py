import numpy as np
from core.data_adapter import lookback_time_gyr, resample_uniform


def test_lookback_monotonic_and_values():
    z = [0.0, 0.5, 1.0, 2.0]
    t, diag = lookback_time_gyr(z)
    assert t.shape == (4,)
    assert all(t[i] <= t[i+1] for i in range(len(t)-1))
    assert diag['min_z'] == 0.0
    assert diag['max_z'] == 2.0


def test_resample_uniform_length_and_bounds():
    t = np.array([0.0, 0.1, 0.5, 1.0])
    y = np.array([1.0, 2.0, 3.0, 2.0])
    dt = 0.2
    t_u, y_u = resample_uniform(t, y, dt)
    assert t_u[0] == 0.0
    assert t_u[-1] >= 1.0
    # Values in range
    assert y_u.min() >= min(y)
    assert y_u.max() <= max(y)


def test_myr_to_s_and_tau_conversion():
    from core.data_adapter import myr_to_s, s_to_myr
    # 1 Myr in seconds
    assert myr_to_s(1.0) == 31557600.0 * 1_000_000.0

    # sample tau: 41.9 Myr -> seconds
    tau_myr = 41.9
    tau_s = myr_to_s(tau_myr)
    # expected approx 1.322e15
    assert abs(tau_s - 1.322e15) / 1.322e15 < 1e-3
    # round-trip
    assert abs(s_to_myr(tau_s) - tau_myr) < 1e-6
