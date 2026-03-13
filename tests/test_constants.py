import math

from core.constants import GRUTParams


def test_phase_i_canonical_constants():
    params = GRUTParams()
    assert math.isclose(params.alpha_vac, 1.0 / 3.0, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(params.screening_S, 108.0 * math.pi, rel_tol=1e-12, abs_tol=0.0)
    assert math.isclose(params.n_g0_sq, 1.0 + params.alpha_vac, rel_tol=0.0, abs_tol=1e-12)
    assert math.isclose(params.n_g0, math.sqrt(1.0 + params.alpha_vac), rel_tol=0.0, abs_tol=1e-12)
