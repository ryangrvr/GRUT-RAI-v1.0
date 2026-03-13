import json

from grut.canon import GRUTCanon
from grut.engine import GRUTEngine


def main() -> None:
    canon = GRUTCanon("canon/grut_canon_v0.2.json")
    engine = GRUTEngine(canon, determinism_mode="STRICT")

    init = {"a": 1.0, "H": 1e-10, "rho": 1e-12, "p": 0.0, "M_X": 0.0}

    outputs, cert = engine.run(
        init,
        run_config={"dt_years": 1e-3, "steps": 1000, "integrator": "RK4"},
        assumption_toggles={"deterministic_run": True, "baseline_eos_p_equals_w_rho": True},
    )

    print("Canon hash:", canon.canon_hash)
    print(json.dumps(cert, indent=2)[:2000], "...\n")

    with open("last_certificate.json", "w", encoding="utf-8") as f:
        json.dump(cert, f, indent=2)

    with open("last_outputs.json", "w", encoding="utf-8") as f:
        json.dump(outputs, f)


if __name__ == "__main__":
    main()
