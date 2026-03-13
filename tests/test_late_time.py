import json

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def approx_equal(a: float, b: float, rel: float = 1e-6, abs_: float = 1e-12) -> bool:
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def test_late_time_expansion_dark_energy_dt_100kyr(tmp_path):
    """
    Integration test: Late-Time Expansion under vacuum-like EOS override (p = -rho).

    Validates:
      1) Robustness at dt=100,000 years (no numerical freeze / crash)
      2) EOS override works (rho stays ~constant because rho+p=0)
      3) Memory stability (M_X tracks sustained driver X = H_base^2)
      4) Deterministic certificate hashes exist
    """
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")

    # Dark-energy-like initial conditions: p = -rho => drho/dt = -3H(rho+p)=0
    init_state = {
        "a": 1.0,
        "rho": 0.2,
        "p": -0.2,
        "H": 1e-10,
        "M_X": 0.0,  # OP_GENESIS should set this
    }

    config = {
        "dt_years": 1e5,
        "steps": 500,  # 50 Myr
        "integrator": "RK4",
    }

    outputs, cert = engine.run(
        init_state,
        run_config=config,
        assumption_toggles={"deterministic_run": True},
    )

    outputs2, cert2 = engine.run(
        init_state,
        run_config=config,
        assumption_toggles={"deterministic_run": True},
    )

    assert cert.get("outputs", {}).get("output_digest") == cert2.get("outputs", {}).get("output_digest")
    assert cert.get("repro_hash") == cert2.get("repro_hash")

    # --- Certificate sanity (deterministic signals, not UUID/timestamp) ---
    assert "engine_signature" in cert
    assert "canon_hash" in cert["engine_signature"]
    assert cert["engine_signature"]["canon_hash"] == canon.canon_hash
    assert "repro_hash" in cert
    assert "outputs" in cert and cert["outputs"].get("output_digest")

    # --- Core outputs sanity ---
    assert "final_state" in outputs
    final = outputs["final_state"]
    assert final["a"] >= 1.0

    hz = outputs["OBS_HZ_001"]
    H_series = hz["H"]
    assert len(H_series) == config["steps"]

    # Must not be identically zero (the “freeze” failure mode)
    assert any(h > 0.0 for h in H_series)

    # --- Physical invariants for this scenario ---
    # rho should remain ~constant (vacuum-like)
    assert approx_equal(final["rho"], 0.2, rel=1e-6, abs_=1e-9)

    # Expansion should be sustained at end (tunable threshold)
    final_H = float(H_series[-1])
    assert final_H > 1e-12

    # Memory should approximately track the driver in steady-state late times.
    # Compute expected driver X_end = H_base^2 from closure at final state:
    C_rho = canon.get_value("C_rho")
    C_k = canon.get_value("C_k")
    K0 = canon.get_value("k0")
    a_end = float(final["a"])
    rho_end = float(final["rho"])
    H_base2_end = (C_rho * rho_end) + (C_k * K0 / (a_end * a_end))

    # M_X should be close to H_base2_end (not exact, but should track)
    M_end = float(final["M_X"])
    # Allow looser tolerance because placeholder model + damping/closure can affect this slightly
    assert approx_equal(M_end, H_base2_end, rel=1e-2, abs_=1e-9)

    # --- Optional plot: do not fail if matplotlib missing ---
    try:
        import matplotlib.pyplot as plt  # optional dependency

        # Plot vs step index (most interpretable here)
        plt.figure()
        plt.plot(range(len(H_series)), H_series)
        plt.xlabel("Step")
        plt.ylabel("H")
        plt.title("Late-Time Expansion (p = -rho, dt=100kyr)")
        out = tmp_path / "test_late_time_H.png"
        plt.savefig(out)
    except Exception:
        pass

    # Write artifacts for manual inspection (useful in VS)
    (tmp_path / "late_time_certificate.json").write_text(json.dumps(cert, indent=2))
    (tmp_path / "late_time_outputs.json").write_text(json.dumps(outputs))
