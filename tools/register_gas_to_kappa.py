from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.cluster_packet import file_sha256
from grut.utils import stable_sha256

try:
    from astropy.io import fits  # type: ignore
    from astropy.wcs import WCS  # type: ignore
except Exception as exc:  # pragma: no cover - optional dependency
    fits = None
    WCS = None

try:
    from reproject import reproject_interp  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    reproject_interp = None


def _require_astropy() -> None:
    if fits is None or WCS is None:
        raise RuntimeError("FITS/WCS support requires astropy")


def _read_fits(path: Path) -> Tuple[np.ndarray, Any]:
    _require_astropy()
    with fits.open(path) as hdul:
        data = hdul[0].data
        header = hdul[0].header
    if data is None:
        raise ValueError(f"FITS file contains no data: {path}")
    return np.array(data, dtype=float), header


def _extract_wcs_fields(header: Any) -> Dict[str, Any]:
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


def _nearest_reproject(
    gas_data: np.ndarray,
    gas_wcs: Any,
    target_wcs: Any,
    target_shape: Tuple[int, int],
) -> np.ndarray:
    ny, nx = target_shape
    y_idx, x_idx = np.indices((ny, nx))
    world = target_wcs.pixel_to_world_values(x_idx, y_idx)
    gx, gy = gas_wcs.world_to_pixel_values(world[0], world[1])
    gx_round = np.rint(gx).astype(int)
    gy_round = np.rint(gy).astype(int)
    out = np.full((ny, nx), np.nan, dtype=float)
    mask = (
        gx_round >= 0
        ) & (gx_round < gas_data.shape[1]) & (gy_round >= 0) & (gy_round < gas_data.shape[0])
    out[mask] = gas_data[gy_round[mask], gx_round[mask]]
    return out


def register_gas_to_kappa(
    kappa_fits_path: Path,
    gas_fits_path: Path,
    outdir: Path,
    method: str = "wcs_reproject",
) -> Dict[str, Any]:
    _require_astropy()
    outdir.mkdir(parents=True, exist_ok=True)

    kappa_data, kappa_header = _read_fits(kappa_fits_path)
    gas_data, gas_header = _read_fits(gas_fits_path)
    kappa_wcs = WCS(kappa_header)
    gas_wcs = WCS(gas_header)

    method_used = method
    if method == "wcs_reproject" and reproject_interp is not None:
        registered, _ = reproject_interp((gas_data, gas_wcs), kappa_wcs, kappa_data.shape)
    else:
        method_used = "nearest_wcs"
        registered = _nearest_reproject(gas_data, gas_wcs, kappa_wcs, kappa_data.shape)

    registered_path = outdir / "gas_registered.npy"
    np.save(registered_path, registered)

    nan_count = int(np.isnan(registered).sum())
    report = {
        "kappa_fits_path": str(kappa_fits_path),
        "gas_fits_path": str(gas_fits_path),
        "method": method_used,
        "shape": list(registered.shape),
        "nan_count": nan_count,
        "kappa_wcs": _extract_wcs_fields(kappa_header),
        "gas_wcs": _extract_wcs_fields(gas_header),
        "hashes": {
            "kappa_fits": file_sha256(str(kappa_fits_path)),
            "gas_fits": file_sha256(str(gas_fits_path)),
            "gas_registered": file_sha256(str(registered_path)),
        },
    }
    report["registration_hash"] = stable_sha256(report)
    report_path = outdir / "registration_report.json"
    report_path.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Register gas FITS to kappa FITS grid")
    parser.add_argument("--kappa_fits_path", required=True)
    parser.add_argument("--gas_fits_path", required=True)
    parser.add_argument("--outdir", default="artifacts/gas_registered")
    parser.add_argument("--method", default="wcs_reproject")
    args = parser.parse_args()

    register_gas_to_kappa(
        Path(args.kappa_fits_path),
        Path(args.gas_fits_path),
        Path(args.outdir),
        method=args.method,
    )


if __name__ == "__main__":
    main()
