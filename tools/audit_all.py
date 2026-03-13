from __future__ import annotations

import csv
import json
import math
import subprocess
import sys
from pathlib import Path
from typing import Iterable, List, Tuple

import numpy as np
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.canon_override import override_canon
from grut.engine import GRUTEngine
from tools.calibrate_and_export import calibrate_and_export


def _run_cmd(cmd: List[str]) -> None:
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def build_profile_packet_cmd(outdir: Path) -> List[str]:
    return [
        sys.executable,
        "tools/run_cluster_profile_packet.py",
        "--kappa_path",
        "artifacts/cluster_sample/kappa.npy",
        "--sigma_baryon_path",
        "artifacts/cluster_sample/kappa.npy",
        "--center_mode",
        "com_positive",
        "--profile_bins",
        "20",
        "--compare_to_model",
        "--model_response",
        "grut_gate_kspace_v0",
        "--k0_policy",
        "r_smooth",
        "--outdir",
        str(outdir),
    ]


def build_cluster_evidence_cmd(outdir: Path) -> List[str]:
    return [
        sys.executable,
        "tools/build_cluster_evidence_packet.py",
        "--cluster",
        "A2744",
        "--model",
        "CATS",
        "--synthetic",
        "--include_gas",
        "--outdir",
        str(outdir),
    ]


def _read_csv_rows(path: Path) -> List[dict]:
    lines = [line for line in path.read_text().splitlines() if not line.startswith("#")]
    if not lines:
        return []
    reader = csv.DictReader(lines)
    return list(reader)


def _assert_monotonic(values: Iterable[float]) -> None:
    values = list(values)
    for prev, curr in zip(values, values[1:]):
        if curr < prev:
            raise ValueError("Values are not monotonic non-decreasing")


def _validate_cosmology_outputs(outputs: dict, steps: int) -> None:
    hz = outputs.get("OBS_HZ_001", {})
    z_vals = list(hz.get("z", []))
    H_vals = list(hz.get("H", []))
    if len(z_vals) != len(H_vals) or len(z_vals) != steps:
        raise ValueError("H(z) array length mismatch")
    if any(not math.isfinite(v) for v in z_vals):
        raise ValueError("Non-finite z values in H(z) output")
    if any(not math.isfinite(v) for v in H_vals):
        raise ValueError("Non-finite H values in H(z) output")

    fs8 = outputs.get("OBS_FS8_001")
    if fs8:
        fs8_vals = list(fs8.get("fsigma8", []))
        fs8_mask = list(fs8.get("fs8_mask", []))
        if len(fs8_vals) != len(z_vals):
            raise ValueError("fsigma8 length mismatch")
        if len(fs8_mask) not in (0, len(z_vals)):
            raise ValueError("fs8_mask length mismatch")
        if not fs8_mask:
            fs8_mask = [False] * len(fs8_vals)
        for v, m in zip(fs8_vals, fs8_mask):
            if m:
                continue
            if v is None or not math.isfinite(float(v)):
                raise ValueError("Non-finite fsigma8 value in unmasked output")


def _cosmology_smoke() -> Tuple[str, str]:
    canon = GRUTCanon("canon/grut_canon_v0.3.json")
    canon = override_canon(canon, {"alpha_mem": 1.0 / 3.0})
    engine = GRUTEngine(canon, determinism_mode="STRICT")
    init_state = {"a": 1.0, "rho": 0.2, "p": 0.0, "rho_m0": 0.2, "H": 1e-10, "M_X": 0.0}
    run_config = {"dt_years": 1e5, "steps": 300, "integrator": "RK4", "start_z": 2.0}

    outputs1, cert1 = engine.run(init_state, run_config=run_config, assumption_toggles={"growth_enabled": True})
    outputs2, cert2 = engine.run(init_state, run_config=run_config, assumption_toggles={"growth_enabled": True})

    if "OBS_HZ_001" not in outputs1 or "OBS_FS8_001" not in outputs1:
        raise ValueError("Missing OBS_HZ_001 or OBS_FS8_001")

    _validate_cosmology_outputs(outputs1, steps=300)

    if cert1.get("outputs", {}).get("output_digest") != cert2.get("outputs", {}).get("output_digest"):
        raise ValueError("Non-deterministic output_digest")
    if cert1.get("repro_hash") != cert2.get("repro_hash"):
        raise ValueError("Non-deterministic repro_hash")

    return cert1.get("engine_signature", {}).get("canon_hash"), cert1.get("repro_hash")


def _conversion_smoke(outdir: Path) -> None:
    manifest = calibrate_and_export(
        canon_path="canon/grut_canon_v0.3.json",
        preset="matter_only",
        alpha_mem=1.0 / 3.0,
        start_z=2.0,
        dt_years=1e5,
        steps=300,
        outdir=str(outdir),
    )
    if manifest.get("status") != "VIABLE":
        raise ValueError("Calibration manifest is not viable")

    ez_path = outdir / "Hz_dimensionless_Ez.csv"
    if not ez_path.exists():
        raise FileNotFoundError("Missing Ez CSV")
    rows = _read_csv_rows(ez_path)
    idx0 = int(manifest.get("idx0"))
    if idx0 >= len(rows):
        raise ValueError("idx0 out of range for Ez CSV")
    ez_val = float(rows[idx0]["E_z"])
    if not math.isclose(ez_val, 1.0, rel_tol=1e-10, abs_tol=0.0):
        raise ValueError("E_z at z0 index is not 1")

    H0_code = float(manifest.get("H0_code"))
    for anchor in manifest.get("anchors", []):
        name = anchor["name"]
        csv_path = outdir / f"Hz_km_s_Mpc_{name}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Missing anchor CSV: {name}")
        scale_H = float(anchor["scale_H"])
        if scale_H <= 0 or not math.isfinite(scale_H):
            raise ValueError("scale_H is non-positive or non-finite")
        expected = float(anchor["H0_km_s_Mpc"]) / H0_code
        if not math.isclose(scale_H, expected, rel_tol=1e-10, abs_tol=0.0):
            raise ValueError("scale_H mismatch H0/H0_code")


def _evidence_packet_smoke(calibration_dir: Path, outdir: Path) -> None:
    packet_path = outdir / "phase2_evidence_packet.json"
    _run_cmd(
        [
            sys.executable,
            "tools/build_evidence_packet.py",
            "--calibration_dir",
            str(calibration_dir),
            "--outdir",
            str(outdir),
        ]
    )
    _run_cmd(
        [
            sys.executable,
            "tools/summarize_evidence_packet.py",
            "--packet",
            str(packet_path),
            "--outdir",
            str(outdir),
        ]
    )

    summary_path = outdir / "summary_table.csv"
    if not summary_path.exists():
        raise FileNotFoundError("Missing summary_table.csv")
    rows = _read_csv_rows(summary_path)
    if not rows:
        raise ValueError("summary_table.csv is empty")
    required = {"component", "path", "sha256", "kind", "size_bytes"}
    if not required.issubset(rows[0].keys()):
        raise ValueError("summary_table.csv missing required columns")


def _quantum_boundary_smoke(outdir: Path, scan_dir: Path) -> None:
    _run_cmd(
        [
            sys.executable,
            "tools/quantum_boundary_test.py",
            "--preset",
            "optomech_micro",
            "--tau0_s",
            "41900000",
            "--omega_policy",
            "controlled",
            "--outdir",
            str(outdir),
        ]
    )
    packet_path = outdir / "quantum_boundary_packet.json"
    if not packet_path.exists():
        raise FileNotFoundError("Missing quantum_boundary_packet.json")
    packet = json.loads(packet_path.read_text())
    outputs = packet.get("outputs", {})
    if "X" not in outputs or "alpha_eff" not in outputs:
        raise ValueError("Quantum boundary outputs missing X or alpha_eff")
    hash_path = outdir / "quantum_boundary_packet.sha256"
    if not hash_path.exists():
        raise FileNotFoundError("Missing quantum_boundary_packet.sha256")

    _run_cmd(
        [
            sys.executable,
            "tools/quantum_boundary_test.py",
            "--preset",
            "optomech_micro",
            "--tau0_s",
            "41900000",
            "--omega_policy",
            "controlled",
            "--scan_omega_min",
            "1e2",
            "--scan_omega_max",
            "1e6",
            "--scan_points",
            "25",
            "--outdir",
            str(scan_dir),
        ]
    )
    scan_path = scan_dir / "quantum_boundary_scan.csv"
    if not scan_path.exists():
        raise FileNotFoundError("Missing quantum_boundary_scan.csv")
    scan_rows = _read_csv_rows(scan_path)
    enhancements = [float(row["enhancement"]) for row in scan_rows]
    _assert_monotonic(enhancements)


def _gaussian_map(n: int, x0: float, y0: float, sigma: float) -> np.ndarray:
    y, x = np.indices((n, n))
    dx = x - x0
    dy = y - y0
    return np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))


def _cluster_prediction_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    n = 64
    sigma_b = _gaussian_map(n, x0=32.0, y0=32.0, sigma=6.0)
    gas = _gaussian_map(n, x0=28.0, y0=32.0, sigma=6.0)

    sigma_path = outdir / "sigma_b.npy"
    gas_path = outdir / "gas.npy"
    np.save(sigma_path, sigma_b)
    np.save(gas_path, gas)

    pred_dir = outdir / "prediction"
    _run_cmd(
        [
            sys.executable,
            "tools/run_cluster_prediction.py",
            "--sigma_baryon_path",
            str(sigma_path),
            "--gas_path",
            str(gas_path),
            "--kernel",
            "k1",
            "--response_model",
            "identity",
            "--alpha_mem",
            "0.333333333",
            "--A_psi",
            "1.0",
            "--fov_arcmin",
            "10",
            "--smoothing_grid",
            "0,1",
            "--threshold_grid",
            "0.1",
            "--peak_mode",
            "com_positive_kappa",
            "--gas_centroid_mode",
            "com_positive",
            "--pixel_scale_arcsec",
            "60",
            "--outdir",
            str(pred_dir),
        ]
    )

    summary_path = pred_dir / "centroids_summary.json"
    cert_path = pred_dir / "nis_prediction_certificate.json"
    offsets_path = pred_dir / "offsets.csv"
    if not summary_path.exists() or not cert_path.exists() or not offsets_path.exists():
        raise FileNotFoundError("Cluster prediction outputs missing")

    summary = json.loads(summary_path.read_text())
    if summary.get("kernel") != "k1":
        raise ValueError("Cluster prediction kernel mismatch")
    if summary.get("response_model") != "identity":
        raise ValueError("Cluster prediction response_model mismatch")
    kappa_stats = summary.get("map_stats", {}).get("kappa", {})
    if not kappa_stats or abs(float(kappa_stats.get("max", 0.0))) < 1e-12:
        raise ValueError("Cluster prediction kappa stats are degenerate")

    cert = json.loads(cert_path.read_text())
    output_digest = cert.get("output_digest")
    if not output_digest:
        raise ValueError("Cluster prediction missing output_digest")


def _cluster_profile_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = build_profile_packet_cmd(outdir)
    _run_cmd(cmd)
    cert_path = outdir / "nis_profile_certificate.json"
    if not cert_path.exists():
        raise FileNotFoundError("Profile packet certificate missing")
    cert_first = json.loads(cert_path.read_text())
    digest_first = cert_first.get("output_digest")
    _run_cmd(cmd)

    metrics_path = outdir / "profile_metrics.json"
    if not metrics_path.exists() or not cert_path.exists():
        raise FileNotFoundError("Profile packet outputs missing")

    metrics = json.loads(metrics_path.read_text())
    rms_diff = float(metrics.get("metrics", {}).get("kappa", {}).get("rms_diff", 0.0))
    if rms_diff <= 0.0:
        raise ValueError("Profile packet rms_diff is not positive")

    cert_second = json.loads(cert_path.read_text())
    digest_second = cert_second.get("output_digest")
    if not digest_first or not digest_second:
        raise ValueError("Profile packet missing output_digest")
    if digest_first != digest_second:
        raise ValueError("Profile packet output_digest is not deterministic")


def _cluster_evidence_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    cmd = build_cluster_evidence_cmd(outdir)
    _run_cmd(cmd)
    packet_path = outdir / "A2744" / "CATS" / "PACKET_INDEX.json"
    if not packet_path.exists():
        raise FileNotFoundError("Missing PACKET_INDEX.json")
    packet_first = json.loads(packet_path.read_text())
    digest_first = packet_first.get("output_digest")
    _run_cmd(cmd)
    packet_second = json.loads(packet_path.read_text())
    digest_second = packet_second.get("output_digest")
    if not digest_first or not digest_second:
        raise ValueError("Cluster evidence packet missing output_digest")
    if digest_first != digest_second:
        raise ValueError("Cluster evidence packet output_digest is not deterministic")
    profile_cert = (
        outdir
        / "A2744"
        / "CATS"
        / "outputs"
        / "profile_packet"
        / "nis_profile_certificate.json"
    )
    if not profile_cert.exists():
        raise FileNotFoundError("Missing profile packet certificate")


def _quantum_evidence_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    run1 = outdir / "run1"
    run2 = outdir / "run2"
    _run_cmd(
        [
            sys.executable,
            "tools/build_quantum_evidence_packet.py",
            "--outdir",
            str(run1),
            "--tau0_s",
            "1.0",
            "--omega_scan_points",
            "5",
            "--mass_scan_points",
            "6",
            "--force",
        ]
    )
    _run_cmd(
        [
            sys.executable,
            "tools/build_quantum_evidence_packet.py",
            "--outdir",
            str(run2),
            "--tau0_s",
            "1.0",
            "--omega_scan_points",
            "5",
            "--mass_scan_points",
            "6",
            "--force",
        ]
    )

    scan_path = run1 / "scans" / "scan_mass_self_consistent.csv"
    if not scan_path.exists():
        raise FileNotFoundError("Missing scan_mass_self_consistent.csv")

    summary_path = run1 / "summary.csv"
    if not summary_path.exists():
        raise FileNotFoundError("Missing summary.csv")
    rows = _read_csv_rows(summary_path)
    if len(rows) < 1:
        raise ValueError("summary.csv missing slope row")

    row = rows[0]
    slope_controlled = float(row["slope_controlled"])
    slope_self = float(row["slope_self_consistent"])
    slope_dp = float(row["slope_dp_reference"])
    if not math.isclose(slope_controlled, -2.0, rel_tol=1e-2, abs_tol=0.0):
        raise ValueError("Controlled slope does not match -2")
    if not math.isclose(slope_self, -2.0 / 3.0, rel_tol=1e-2, abs_tol=0.0):
        raise ValueError("Self-consistent slope does not match -2/3")
    if not math.isclose(slope_dp, -2.0, rel_tol=1e-2, abs_tol=0.0):
        raise ValueError("DP slope does not match -2")

    cert1 = json.loads((run1 / "nis_quantum_certificate.json").read_text())
    cert2 = json.loads((run2 / "nis_quantum_certificate.json").read_text())
    if cert1.get("output_digest") != cert2.get("output_digest"):
        raise ValueError("Quantum evidence packet output_digest is not deterministic")


def _hubble_tension_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    windows = ["full", "z_le_1_0"]
    for window_policy in windows:
        run1 = outdir / f"run1_{window_policy}"
        run2 = outdir / f"run2_{window_policy}"
        _run_cmd(
            [
                sys.executable,
                "tools/build_hubble_tension_packet.py",
                "--outdir",
                str(run1),
                "--steps",
                "60",
                "--dt_years",
                "100000.0",
                "--start_z",
                "2.0",
                "--include_vacuum_plus_matter",
                "true",
                "--dataset_policy",
                "min",
                "--compare_window_policy",
                window_policy,
                "--preset",
                "matter_only",
                "--recommendation_mode",
                "late_time_grid",
            ]
        )
        _run_cmd(
            [
                sys.executable,
                "tools/build_hubble_tension_packet.py",
                "--outdir",
                str(run2),
                "--steps",
                "60",
                "--dt_years",
                "100000.0",
                "--start_z",
                "2.0",
                "--include_vacuum_plus_matter",
                "true",
                "--dataset_policy",
                "min",
                "--compare_window_policy",
                window_policy,
                "--preset",
                "matter_only",
                "--recommendation_mode",
                "late_time_grid",
            ]
        )
        rec_path = run1 / "outputs" / "late_time_recommendation.json"
        if not rec_path.exists():
            raise FileNotFoundError("Missing late_time_recommendation.json")
        rec = json.loads(rec_path.read_text())
        candidates = rec.get("candidates", [])
        if len(candidates) < 3:
            raise ValueError("late_time_recommendation.json has insufficient candidates")
        cert1 = json.loads((run1 / "nis_hubble_certificate.json").read_text())
        cert2 = json.loads((run2 / "nis_hubble_certificate.json").read_text())
        if cert1.get("output_digest") != cert2.get("output_digest"):
            raise ValueError(f"Hubble tension packet output_digest is not deterministic for {window_policy}")


def _rotation_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    data_path = outdir / "galaxy.csv"
    data_path.write_text(
        "r_kpc,v_obs,v_err,v_gas,v_star\n"
        "1,110,5,60,80\n"
        "2,110,5,60,80\n"
        "3,110,5,60,80\n"
        "4,110,5,60,80\n"
    )

    packet_dir = outdir / "packet"
    _run_cmd(
        [
            sys.executable,
            "tools/run_rotation_packet.py",
            "--data_path",
            str(data_path),
            "--response_model",
            "radial_gate_v0",
            "--alpha_mem",
            "0.2",
            "--r0_policy",
            "median_radius",
            "--outdir",
            str(packet_dir),
        ]
    )

    metrics_path = packet_dir / data_path.stem / "metrics.json"
    cert_path = packet_dir / data_path.stem / "nis_rotation_certificate.json"
    if not metrics_path.exists() or not cert_path.exists():
        raise FileNotFoundError("Rotation packet outputs missing")

    cert_first = json.loads(cert_path.read_text())
    digest_first = cert_first.get("output_digest")
    _run_cmd(
        [
            sys.executable,
            "tools/run_rotation_packet.py",
            "--data_path",
            str(data_path),
            "--response_model",
            "radial_gate_v0",
            "--alpha_mem",
            "0.2",
            "--r0_policy",
            "median_radius",
            "--outdir",
            str(packet_dir),
        ]
    )
    cert_second = json.loads(cert_path.read_text())
    digest_second = cert_second.get("output_digest")
    if digest_first != digest_second:
        raise ValueError("Rotation packet output_digest is not deterministic")


def _rotation_batch_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    data_dir = outdir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    data1 = data_dir / "g1.csv"
    data2 = data_dir / "g2.csv"
    header = "r_kpc,v_obs,v_err,v_gas,v_star\n"
    data1.write_text(header + "1,100,5,60,80\n2,100,5,60,80\n")
    data2.write_text(header + "1,90,5,50,70\n2,90,5,50,70\n")

    batch_out = outdir / "batch"
    _run_cmd(
        [
            sys.executable,
            "tools/run_rotation_batch.py",
            "--datadir",
            str(data_dir),
            "--glob",
            "*.csv",
            "--response_model",
            "identity",
            "--r0_policy",
            "median_radius",
            "--outdir",
            str(batch_out),
        ]
    )

    summary_path = batch_out / "summary.csv"
    manifest_path = batch_out / "batch_manifest.json"
    if not summary_path.exists() or not manifest_path.exists():
        raise FileNotFoundError("Rotation batch outputs missing")

    manifest1 = json.loads(manifest_path.read_text())
    _run_cmd(
        [
            sys.executable,
            "tools/run_rotation_batch.py",
            "--datadir",
            str(data_dir),
            "--glob",
            "*.csv",
            "--response_model",
            "identity",
            "--r0_policy",
            "median_radius",
            "--outdir",
            str(batch_out),
        ]
    )
    manifest2 = json.loads(manifest_path.read_text())
    if manifest1.get("summary_hash") != manifest2.get("summary_hash"):
        raise ValueError("Rotation batch summary_hash is not deterministic")


def _cluster_offset_packet_smoke(outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    kappa = _gaussian_map(64, x0=32.0, y0=32.0, sigma=6.0)
    gas = _gaussian_map(64, x0=36.0, y0=32.0, sigma=6.0)

    kappa_path = outdir / "kappa.npy"
    gas_path = outdir / "gas.npy"
    np.save(kappa_path, kappa)
    np.save(gas_path, gas)

    packet_dir = outdir / "packet"
    _run_cmd(
        [
            sys.executable,
            "tools/run_cluster_offset_packet.py",
            "--kappa_path",
            str(kappa_path),
            "--gas_path",
            str(gas_path),
            "--pixel_scale_arcsec",
            "1.0",
            "--smoothing_grid",
            "0",
            "--threshold_grid",
            "0.1",
            "--outdir",
            str(packet_dir),
        ]
    )

    summary_path = packet_dir / "centroids_summary.json"
    cert_path = packet_dir / "nis_cluster_offset_certificate.json"
    if not summary_path.exists() or not cert_path.exists():
        raise FileNotFoundError("Cluster offset packet outputs missing")

    cert_first = json.loads(cert_path.read_text())
    digest_first = cert_first.get("output_digest")
    _run_cmd(
        [
            sys.executable,
            "tools/run_cluster_offset_packet.py",
            "--kappa_path",
            str(kappa_path),
            "--gas_path",
            str(gas_path),
            "--pixel_scale_arcsec",
            "1.0",
            "--smoothing_grid",
            "0",
            "--threshold_grid",
            "0.1",
            "--outdir",
            str(packet_dir),
        ]
    )
    cert_second = json.loads(cert_path.read_text())
    digest_second = cert_second.get("output_digest")
    if digest_first != digest_second:
        raise ValueError("Cluster offset packet output_digest is not deterministic")


def main() -> None:
    _run_cmd([sys.executable, "-m", "pytest", "-q"])

    canon_hash, repro_hash = _cosmology_smoke()

    audit_dir = Path("artifacts/audit")
    calib_dir = audit_dir / "calibration"
    _conversion_smoke(calib_dir)

    evidence_dir = audit_dir / "evidence_packet"
    _evidence_packet_smoke(calibration_dir=calib_dir, outdir=evidence_dir)

    qb_dir = audit_dir / "quantum_boundary"
    qb_scan_dir = audit_dir / "quantum_boundary_scan"
    _quantum_boundary_smoke(qb_dir, qb_scan_dir)

    quantum_packet_dir = audit_dir / "quantum_evidence_packet"
    _quantum_evidence_packet_smoke(quantum_packet_dir)

    hubble_packet_dir = audit_dir / "hubble_tension_packet"
    _hubble_tension_packet_smoke(hubble_packet_dir)

    rotation_dir = audit_dir / "rotation_packet"
    _rotation_packet_smoke(rotation_dir)

    rotation_batch_dir = audit_dir / "rotation_batch"
    _rotation_batch_smoke(rotation_batch_dir)

    cluster_offset_dir = audit_dir / "cluster_offset_packet"
    _cluster_offset_packet_smoke(cluster_offset_dir)

    cluster_pred_dir = audit_dir / "cluster_prediction"
    _cluster_prediction_smoke(cluster_pred_dir)

    profile_dir = Path("artifacts/_audit_profile_packet")
    _cluster_profile_packet_smoke(profile_dir)

    evidence_dir = Path("artifacts/_audit_cluster_evidence")
    _cluster_evidence_packet_smoke(evidence_dir)

    print("AUDIT PASS")
    print(f"canon_hash: {canon_hash}")
    print(f"repro_hash: {repro_hash}")


if __name__ == "__main__":
    main()