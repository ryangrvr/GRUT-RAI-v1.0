from __future__ import annotations

import numpy as np

from grut.rotation_curves import compute_v_grut


def test_response_models_nontrivial():
    r = np.linspace(1, 10, 10)
    v_bar = np.linspace(80, 100, 10)

    v_identity, _ = compute_v_grut(v_bar, r, response_model="identity")
    v_gate, meta_gate = compute_v_grut(
        v_bar,
        r,
        response_model="radial_gate_v0",
        alpha_mem=0.2,
        r0_policy="median_radius",
    )
    v_boost, meta_boost = compute_v_grut(
        v_bar,
        r,
        response_model="memory_scale_boost_v0",
        alpha_mem=0.2,
        r0_policy="median_radius",
    )

    assert not np.allclose(v_identity, v_gate)
    assert not np.allclose(v_identity, v_boost)
    assert meta_gate["r0_policy"] == "median_radius"
    assert meta_boost["r0_policy"] == "median_radius"
