from __future__ import annotations

import numpy as np

from grut.quantum import fit_loglog_slope


def test_loglog_slope_power_law() -> None:
    masses = np.logspace(-12, -6, 20)
    t_dec = 3.7 * masses ** (-2.0 / 3.0)
    slope, _ = fit_loglog_slope(masses, t_dec)
    assert np.isclose(slope, -2.0 / 3.0, rtol=1e-6)
