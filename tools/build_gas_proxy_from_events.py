from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from grut.cluster_packet import file_sha256
from grut.utils import stable_sha256

try:
    from astropy.io import fits  # type: ignore
    from astropy.wcs import WCS  # type: ignore
except Exception as exc:  # pragma: no cover
    fits = None
    WCS = None

try:
    from reproject import reproject_interp  # type: ignore
except Exception:  # pragma: no cover
    reproject_interp = None


def _require_astropy() -> None:
    if fits is None or WCS is None:
        raise RuntimeError("FITS/WCS support requires astropy")


def _find_event_files(obs_dir: Path) -> List[Path]:
    candidates = []
    for pattern in ("*evt2*.fits", "*evt3*.fits", "*evt*.fits"):
        candidates.extend(obs_dir.rglob(pattern))
    return [p for p in candidates if p.is_file()]


def _select_event_file(obs_dir: Path) -> Optional[Path]:
    files = _find_event_files(obs_dir)
    if not files:
        return None
    def score(p: Path) -> int:
        name = p.name.lower()
        if "evt3" in name:
            return 3
        if "evt2" in name:
            return 2
        return 1
    return sorted(files, key=score, reverse=True)[0]


def _extract_events(path: Path) -> Tuple[np.ndarray, np.ndarray, Optional[np.ndarray], Any]:
    _require_astropy()
    with fits.open(path) as hdul:
        data = hdul[1].data
        header = hdul[1].header
    x = np.array(data["X"], dtype=float)
    y = np.array(data["Y"], dtype=float)
    energy = None
    if "ENERGY" in data.columns.names:
        energy = np.array(data["ENERGY"], dtype=float)
    return x, y, energy, header


def _filter_energy(
    x: np.ndarray,
    y: np.ndarray,
    energy: Optional[np.ndarray],
    band_keV: Optional[Tuple[float, float]],
) -> Tuple[np.ndarray, np.ndarray, str]:
    if energy is None or band_keV is None:
        return x, y, "none"
    energy_keV = energy
    if np.nanmax(energy) > 100.0:
        energy_keV = energy / 1000.0
    lo, hi = band_keV
    mask = (energy_keV >= lo) & (energy_keV <= hi)
    return x[mask], y[mask], f"{lo}-{hi} keV"


def _bin_events(x: np.ndarray, y: np.ndarray, bin_size_px: float) -> Tuple[np.ndarray, float, float]:
    x_min = np.floor(np.min(x)).astype(int)
    y_min = np.floor(np.min(y)).astype(int)
    x_max = np.ceil(np.max(x)).astype(int)
    y_max = np.ceil(np.max(y)).astype(int)
    bins_x = int(np.ceil((x_max - x_min + 1) / bin_size_px))
    bins_y = int(np.ceil((y_max - y_min + 1) / bin_size_px))
    hist, _, _ = np.histogram2d(
        y,
        x,
        bins=[bins_y, bins_x],
        range=[[y_min, y_min + bins_y * bin_size_px], [x_min, x_min + bins_x * bin_size_px]],
    )
    return hist.astype(float), float(x_min), float(y_min)


def _reproject_to_target(
    image: np.ndarray,
    source_wcs: Any,
    target_wcs: Any,
    target_shape: Tuple[int, int],
) -> np.ndarray:
    if reproject_interp is not None:
        out, _ = reproject_interp((image, source_wcs), target_wcs, target_shape)
        return out
    return image


def build_gas_proxy(
    obs_root: Path,
    outdir: Path,
    bin_arcsec: float = 1.0,
    energy_band_keV: Optional[Tuple[float, float]] = None,
) -> Dict[str, Any]:
    _require_astropy()
    outdir.mkdir(parents=True, exist_ok=True)

    obs_dirs = sorted([p for p in obs_root.glob("obsid_*") if p.is_dir()])
    if not obs_dirs:
        raise ValueError(f"No obsid_* folders found in {obs_root}")

    combined = None
    target_wcs = None
    report_obs = []
    for obs_dir in obs_dirs:
        evt_path = _select_event_file(obs_dir)
        if evt_path is None:
            continue
        x, y, energy, header = _extract_events(evt_path)
        x, y, energy_filter = _filter_energy(x, y, energy, energy_band_keV)
        wcs = WCS(header)
        pixel_scale_arcsec = abs(header.get("CDELT1", -1.0 / 3600.0)) * 3600.0
        bin_size_px = max(1.0, float(bin_arcsec) / float(pixel_scale_arcsec))
        image, x_min, y_min = _bin_events(x, y, bin_size_px)
        if target_wcs is None:
            target_wcs = wcs
            combined = image
        else:
            image = _reproject_to_target(image, wcs, target_wcs, combined.shape)
            combined = combined + image
        report_obs.append(
            {
                "obsid": obs_dir.name.replace("obsid_", ""),
                "event_file": str(evt_path),
                "energy_filter": energy_filter,
                "bin_arcsec": bin_arcsec,
                "pixel_scale_arcsec": pixel_scale_arcsec,
            }
        )

    if combined is None or target_wcs is None:
        raise ValueError("No event files found to build gas proxy")

    gas_path = outdir / "gas_counts.fits"
    hdu = fits.PrimaryHDU(data=combined, header=target_wcs.to_header())
    hdu.writeto(gas_path, overwrite=True)

    report = {
        "obs_root": str(obs_root),
        "bin_arcsec": bin_arcsec,
        "energy_band_keV": list(energy_band_keV) if energy_band_keV else None,
        "obsids": report_obs,
        "outputs": {
            "gas_counts_fits": str(gas_path),
            "gas_counts_sha256": file_sha256(str(gas_path)),
        },
    }
    report["build_hash"] = stable_sha256(report)
    report_path = outdir / "BUILD_REPORT.json"
    report_path.write_text(json.dumps(report, indent=2))

    certificate = {
        "tool_version": "v0.6B",
        "determinism_mode": "STRICT",
        "input_hash": stable_sha256({"obs_root": str(obs_root), "bin_arcsec": bin_arcsec}),
        "output_hashes": {"gas_counts.fits": file_sha256(str(gas_path)), "BUILD_REPORT.json": file_sha256(str(report_path))},
    }
    certificate["output_digest"] = stable_sha256(certificate["output_hashes"])
    (outdir / "nis_gas_proxy_certificate.json").write_text(json.dumps(certificate, indent=2))
    return {"report": report, "certificate": certificate}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build gas proxy from Chandra events")
    parser.add_argument("--obs_root", default="artifacts/chandra_raw/A2744")
    parser.add_argument("--indir", default=None)
    parser.add_argument("--outdir", default="artifacts/gas_proxy/A2744")
    parser.add_argument("--bin_arcsec", type=float, default=1.0)
    parser.add_argument("--energy_band_keV", nargs=2, type=float, default=None)
    args = parser.parse_args()

    obs_root = Path(args.indir) if args.indir else Path(args.obs_root)
    energy_band = tuple(args.energy_band_keV) if args.energy_band_keV else None
    build_gas_proxy(obs_root, Path(args.outdir), bin_arcsec=args.bin_arcsec, energy_band_keV=energy_band)


if __name__ == "__main__":
    main()
