import numpy as np

from grut.lensing import make_grid, spectral_derivatives_2d


def test_spectral_derivatives_scaling():
    n = 64
    fov_arcmin = 20.0
    fov_rad = fov_arcmin / (206264.806 / 60.0)
    theta_x, theta_y = make_grid(n, fov_rad)
    L = fov_rad
    k = 2.0 * np.pi / L

    psi = np.sin(k * theta_x) + np.cos(k * theta_y)
    dx_true = k * np.cos(k * theta_x)
    dy_true = -k * np.sin(k * theta_y)
    dxx_true = -(k**2) * np.sin(k * theta_x)
    dyy_true = -(k**2) * np.cos(k * theta_y)
    dxy_true = np.zeros_like(psi)

    dx, dy, dxx, dyy, dxy = spectral_derivatives_2d(psi, fov_rad)

    assert np.max(np.abs(dx - dx_true)) < 1e-6
    assert np.max(np.abs(dy - dy_true)) < 1e-6
    assert np.max(np.abs(dxx - dxx_true)) < 1e-6
    assert np.max(np.abs(dyy - dyy_true)) < 1e-6
    assert np.max(np.abs(dxy - dxy_true)) < 1e-6