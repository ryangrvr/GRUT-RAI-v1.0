from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.canon import GRUTCanon
from grut.cluster_packet import file_sha256, load_map
from grut.utils import stable_sha256
from tools.run_cluster_profile_packet import run_cluster_profile_packet
from tools.register_gas_to_kappa import register_gas_to_kappa
from tools.build_gas_proxy_from_events import build_gas_proxy


try:
    from astropy.io import fits  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    fits = None


def _require_astropy() -> None:
    if fits is None:
        raise RuntimeError("FITS support requires astropy")


def _load_array(path: Path) -> np.ndarray:
    if path.suffix == ".npy":
        return np.load(path)
    _require_astropy()
    with fits.open(path) as hdul:
        data = hdul[0].data
        if data is None:
            raise ValueError(f"FITS file contains no data: {path}")
        arr = np.array(data, dtype=float)
    return np.squeeze(arr)


def _write_fits(path: Path, data: np.ndarray) -> None:
    _require_astropy()
    hdu = fits.PrimaryHDU(data)
    hdu.writeto(path, overwrite=True)


def _center_crop_square(values: np.ndarray) -> np.ndarray:
    if values.ndim != 2:
        return values
    ny, nx = values.shape
    if ny == nx:
        return values
    n = min(ny, nx)
    y0 = (ny - n) // 2
    x0 = (nx - n) // 2
    return values[y0 : y0 + n, x0 : x0 + n]


def _extract_wcs(path: Path) -> Dict[str, Any]:
    if path.suffix == ".npy":
        return {}
    _require_astropy()
    with fits.open(path) as hdul:
        header = hdul[0].header
    keys = [
        "CRPIX1",
        "CRPIX2",
        "CRVAL1",
        "CRVAL2",
        "CDELT1",
        "CDELT2",
        "CD1_1",
        "CD1_2",
        "CD2_1",
        "CD2_2",
        "CTYPE1",
        "CTYPE2",
    ]
    return {k: header.get(k) for k in keys if k in header}


def _copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(src.read_bytes())


def _write_packet_index(outdir: Path, payload: Dict[str, Any]) -> None:
    (outdir / "PACKET_INDEX.json").write_text(json.dumps(payload, indent=2))


def _write_readme(outdir: Path, payload: Dict[str, Any]) -> None:
    text = """# Cluster Evidence Packet v0.6A

This packet contains HFF lens-model products (model-derived maps). No fitting is performed.

- Raw inputs: lens model FITS maps (kappa/gamma)
- Processed: numpy arrays + WCS summary
- Outputs: v0.5 profile packet

Repro steps are listed in PACKET_INDEX.json.
"""
    (outdir / "README_DATA.md").write_text(text)


def _parse_bool(value: Optional[str]) -> bool:
    if value is None:
        return False
    value = str(value).strip().lower()
    return value in {"1", "true", "yes", "y", "on"}


def _build_synthetic(raw_dir: Path) -> Dict[str, Path]:
    raw_dir.mkdir(parents=True, exist_ok=True)
    n = 64
    y, x = np.indices((n, n))
    dx = x - n / 2
    dy = y - n / 2
    sigma = 6.0
    kappa = np.exp(-(dx * dx + dy * dy) / (2.0 * sigma * sigma))
    gamma1 = np.zeros_like(kappa)
    gamma2 = np.zeros_like(kappa)
    gas = np.exp(-(((dx - 4.0) ** 2 + (dy + 3.0) ** 2) / (2.0 * sigma * sigma)))
    if fits is None:
        kappa_path = raw_dir / "kappa.npy"
        gamma1_path = raw_dir / "gamma1.npy"
        gamma2_path = raw_dir / "gamma2.npy"
        gas_path = raw_dir / "gas.npy"
        np.save(kappa_path, kappa)
        np.save(gamma1_path, gamma1)
        np.save(gamma2_path, gamma2)
        np.save(gas_path, gas)
    else:
        kappa_path = raw_dir / "kappa.fits"
        gamma1_path = raw_dir / "gamma1.fits"
        gamma2_path = raw_dir / "gamma2.fits"
        gas_path = raw_dir / "gas.fits"
        _write_fits(kappa_path, kappa)
        _write_fits(gamma1_path, gamma1)
        _write_fits(gamma2_path, gamma2)
        _write_fits(gas_path, gas)
    provenance = {
        "mode": "synthetic",
        "files": {
            "kappa": kappa_path.name,
            "gamma1": gamma1_path.name,
            "gamma2": gamma2_path.name,
            "gas": gas_path.name,
        },
    }
    (raw_dir / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2))
    return {"kappa": kappa_path, "gamma1": gamma1_path, "gamma2": gamma2_path, "gas": gas_path}


def build_cluster_evidence_packet(config: Dict[str, Any], outdir: str) -> Dict[str, Any]:
    cluster = config.get("cluster")
    model = config.get("model")
    outdir_path = Path(outdir) / cluster / model
    outdir_path.mkdir(parents=True, exist_ok=True)

    raw_root = Path(config.get("raw_root", "artifacts/hff_raw"))
    raw_dir = raw_root / cluster / model
    synthetic = bool(config.get("synthetic", False))
    include_gas = bool(config.get("include_gas", False))
    gas_fits_path = config.get("gas_fits_path")
    gas_from_chandra = bool(config.get("gas_from_chandra_a2744", False))

    if synthetic:
        raw_dir = outdir_path / "raw"
        paths = _build_synthetic(raw_dir)
        if include_gas:
            gas_fits_path = str(paths.get("gas")) if paths.get("gas") else None
    else:
        gamma_fallback = raw_dir / "selected/gamma.fits"
        gamma1_path = Path(config.get("gamma1_fits_path") or raw_dir / "selected/gamma1.fits")
        gamma2_path = Path(config.get("gamma2_fits_path") or raw_dir / "selected/gamma2.fits")
        if not gamma1_path.exists() and gamma_fallback.exists():
            gamma1_path = gamma_fallback
        if not gamma2_path.exists() and gamma_fallback.exists():
            gamma2_path = gamma_fallback
        paths = {
            "kappa": Path(config.get("kappa_fits_path") or raw_dir / "selected/kappa.fits"),
            "gamma1": gamma1_path,
            "gamma2": gamma2_path,
        }

    raw_out = outdir_path / "raw"
    raw_out.mkdir(parents=True, exist_ok=True)
    for key, path in paths.items():
        _copy(path, raw_out / path.name)
    if (raw_dir / "PROVENANCE.json").exists():
        _copy(raw_dir / "PROVENANCE.json", raw_out / "PROVENANCE.json")
    if gas_from_chandra:
        chandra_root = Path("artifacts/chandra_raw/A2744")
        gas_proxy_dir = outdir_path / "processed/gas_proxy"
        gas_proxy_dir.mkdir(parents=True, exist_ok=True)
        gas_proxy = build_gas_proxy(chandra_root, gas_proxy_dir)
        gas_fits_path = str(gas_proxy_dir / "gas_counts.fits")

    if gas_fits_path:
        gas_path = Path(gas_fits_path)
        gas_out = raw_out / "gas"
        gas_out.mkdir(parents=True, exist_ok=True)
        _copy(gas_path, gas_out / gas_path.name)
        gas_prov = {
            "gas_fits_path": str(gas_path),
            "gas_hash": file_sha256(str(gas_path)),
        }
        (gas_out / "GAS_PROVENANCE.json").write_text(json.dumps(gas_prov, indent=2))

    processed = outdir_path / "processed"
    processed.mkdir(parents=True, exist_ok=True)
    kappa = _center_crop_square(_load_array(paths["kappa"]))
    gamma1 = _center_crop_square(_load_array(paths["gamma1"])) if paths.get("gamma1") and paths["gamma1"].exists() else None
    gamma2 = _center_crop_square(_load_array(paths["gamma2"])) if paths.get("gamma2") and paths["gamma2"].exists() else None
    if gamma1 is not None and gamma2 is None and gamma1.ndim == 3 and gamma1.shape[0] == 2:
        gamma2 = gamma1[1]
        gamma1 = gamma1[0]

    np.save(processed / "kappa.npy", kappa)
    if gamma1 is not None:
        np.save(processed / "gamma1.npy", gamma1)
    if gamma2 is not None:
        np.save(processed / "gamma2.npy", gamma2)

    wcs = _extract_wcs(paths["kappa"])
    (processed / "WCS.json").write_text(json.dumps(wcs, indent=2))

    pixel_scale_arcsec = None
    if "CDELT1" in wcs:
        pixel_scale_arcsec = abs(float(wcs["CDELT1"])) * 3600.0
    pixel_scale_arcsec = pixel_scale_arcsec or float(config.get("pixel_scale_arcsec", 1.0))
    fov_arcmin = (pixel_scale_arcsec * kappa.shape[0]) / 60.0

    outputs_dir = outdir_path / "outputs/profile_packet"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    profile_config = {
        "kappa_path": str(processed / "kappa.npy"),
        "gamma1_path": str(processed / "gamma1.npy") if gamma1 is not None else None,
        "gamma2_path": str(processed / "gamma2.npy") if gamma2 is not None else None,
        "sigma_baryon_path": str(processed / "kappa.npy"),
        "center_mode": "com_positive",
        "profile_bins": 20,
        "compare_to_model": True,
        "model_response": "grut_gate_kspace_v0",
        "k0_policy": "r_smooth",
        "pixel_scale_arcsec": pixel_scale_arcsec,
        "fov_arcmin": fov_arcmin,
        "smoothing_grid": [1.0],
    }
    profile_result = run_cluster_profile_packet(profile_config, str(outputs_dir))

    gas_offset_outputs = None
    if gas_fits_path:
        gas_reg_dir = outdir_path / "processed/gas_registered"
        gas_reg_dir.mkdir(parents=True, exist_ok=True)
        registration_report = register_gas_to_kappa(
            Path(paths["kappa"]),
            Path(gas_fits_path),
            gas_reg_dir,
            method="wcs_reproject",
        )
        gas_offset_dir = outdir_path / "outputs/gas_offset_packet"
        gas_offset_dir.mkdir(parents=True, exist_ok=True)
        gas_offset_config = {
            "kappa_path": str(processed / "kappa.npy"),
            "gas_path": str(gas_reg_dir / "gas_registered.npy"),
            "smoothing_grid": [0.0, 1.0, 2.0],
            "threshold_grid": [0.0, 0.1],
            "peak_mode": "com_positive_kappa",
            "gas_centroid_mode": "com_positive",
            "normalize_mode": "none",
            "pixel_scale_arcsec": pixel_scale_arcsec,
        }
        from tools.run_cluster_offset_packet import run_cluster_offset_packet

        gas_offset_outputs = run_cluster_offset_packet(gas_offset_config, str(gas_offset_dir))
        (gas_offset_dir / "registration_report.json").write_text(
            json.dumps(registration_report, indent=2)
        )

    packet_files = {
        "raw": [str(p.relative_to(outdir_path)) for p in raw_out.rglob("*") if p.is_file()],
        "processed": [str(p.relative_to(outdir_path)) for p in processed.rglob("*") if p.is_file()],
        "outputs": [str(p.relative_to(outdir_path)) for p in outputs_dir.rglob("*") if p.is_file()],
    }
    if gas_fits_path:
        packet_files["outputs_gas"] = [
            str(p.relative_to(outdir_path))
            for p in (outdir_path / "outputs/gas_offset_packet").rglob("*")
            if p.is_file()
        ]
    output_hashes = {
        "profiles.csv": file_sha256(str(outputs_dir / "profiles.csv")),
        "profile_metrics.json": file_sha256(str(outputs_dir / "profile_metrics.json")),
        "nis_profile_certificate.json": file_sha256(str(outputs_dir / "nis_profile_certificate.json")),
    }
    if gas_fits_path:
        gas_offset_dir = outdir_path / "outputs/gas_offset_packet"
        output_hashes.update(
            {
                "gas_offsets.csv": file_sha256(str(gas_offset_dir / "offsets.csv")),
                "gas_centroids_summary.json": file_sha256(
                    str(gas_offset_dir / "centroids_summary.json")
                ),
                "nis_cluster_offset_certificate.json": file_sha256(
                    str(gas_offset_dir / "nis_cluster_offset_certificate.json")
                ),
                "gas_registration_report.json": file_sha256(
                    str(gas_offset_dir / "registration_report.json")
                ),
            }
        )
    output_digest = stable_sha256(output_hashes)

    canon_hash = GRUTCanon("canon/grut_canon_v0.3.json").canon_hash
    packet_index = {
        "cluster": cluster,
        "model": model,
        "synthetic": synthetic,
        "gas_fits_path": gas_fits_path,
        "gas_from_chandra_a2744": gas_from_chandra,
        "packet_files": packet_files,
        "output_hashes": output_hashes,
        "output_digest": output_digest,
        "profile_packet_certificate": profile_result.get("certificate"),
        "gas_offset_packet": gas_offset_outputs,
        "canon_hash": canon_hash,
    }
    _write_packet_index(outdir_path, packet_index)
    _write_readme(outdir_path, packet_index)

    return packet_index


def main() -> None:
    parser = argparse.ArgumentParser(description="Build cluster evidence packet v0.6A")
    parser.add_argument("--cluster", default="A2744")
    parser.add_argument("--model", default="CATS")
    parser.add_argument("--raw_root", default="artifacts/hff_raw")
    parser.add_argument("--kappa_fits_path")
    parser.add_argument("--gamma1_fits_path")
    parser.add_argument("--gamma2_fits_path")
    parser.add_argument("--outdir", default="artifacts/evidence_cluster_v0_6A")
    parser.add_argument("--synthetic", action="store_true")
    parser.add_argument("--gas_fits_path")
    parser.add_argument("--include_gas", action="store_true")
    parser.add_argument("--gas_from_chandra_a2744", nargs="?", const="true", default="false")
    parser.add_argument("--pixel_scale_arcsec", type=float, default=1.0)
    args = parser.parse_args()

    outdir = Path(args.outdir)
    config = {
        "cluster": args.cluster,
        "model": args.model,
        "raw_root": args.raw_root,
        "kappa_fits_path": args.kappa_fits_path,
        "gamma1_fits_path": args.gamma1_fits_path,
        "gamma2_fits_path": args.gamma2_fits_path,
        "synthetic": args.synthetic,
        "gas_fits_path": args.gas_fits_path,
        "include_gas": args.include_gas,
        "gas_from_chandra_a2744": _parse_bool(args.gas_from_chandra_a2744),
        "pixel_scale_arcsec": args.pixel_scale_arcsec,
    }
    build_cluster_evidence_packet(config, str(outdir))


if __name__ == "__main__":
    main()
