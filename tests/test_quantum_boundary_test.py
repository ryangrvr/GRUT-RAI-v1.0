import math

import pytest

from grut.quantum import QuantumBoundaryError, compute_boundary, compute_scan_rows_omega
from tools.quantum_boundary_test import build_packet


def test_controlled_requires_omega():
    with pytest.raises(QuantumBoundaryError):
        compute_boundary(
            m_kg=1.0,
            l_m=1.0,
            tau0_s=1.0,
            omega_policy="controlled",
            omega_exp=None,
            alpha_vac=1.0 / 3.0,
        )


def test_determinism_hash_stable():
    inputs, outputs = compute_boundary(
        m_kg=2.0,
        l_m=0.5,
        tau0_s=10.0,
        omega_policy="controlled",
        omega_exp=0.25,
        alpha_vac=1.0 / 3.0,
    )
    packet1 = build_packet(inputs, outputs)
    packet2 = build_packet(inputs, outputs)
    assert packet1 == packet2


def test_enhancement_large_x():
    inputs, outputs = compute_boundary(
        m_kg=1.0,
        l_m=1.0,
        tau0_s=1.0,
        omega_policy="controlled",
        omega_exp=1e6,
        alpha_vac=1.0 / 3.0,
    )
    assert math.isfinite(outputs["enhancement"])
    assert outputs["enhancement"] > 1.0


def test_scan_deterministic_and_monotonic():
    rows1 = compute_scan_rows_omega(
        m_kg=1.0,
        l_m=1.0,
        tau0_s=10.0,
        alpha_vac=1.0 / 3.0,
        omega_min=1.0,
        omega_max=10.0,
        scan_points=5,
    )
    rows2 = compute_scan_rows_omega(
        m_kg=1.0,
        l_m=1.0,
        tau0_s=10.0,
        alpha_vac=1.0 / 3.0,
        omega_min=1.0,
        omega_max=10.0,
        scan_points=5,
    )
    assert rows1 == rows2

    enhancements = [row["enhancement"] for row in rows1]
    assert enhancements == sorted(enhancements)