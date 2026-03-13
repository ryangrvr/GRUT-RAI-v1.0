import json
import numpy as np

from tools.build_gas_proxy_from_events import build_gas_proxy

try:
    from astropy.io import fits  # type: ignore
    from astropy.table import Table  # type: ignore
except Exception:  # pragma: no cover
    fits = None
    Table = None


def test_build_gas_proxy_from_events(tmp_path):
    if fits is None or Table is None:
        return

    obs_dir = tmp_path / "obsid_0001"
    obs_dir.mkdir(parents=True, exist_ok=True)

    n = 50
    rng = np.random.default_rng(42)
    x = rng.normal(loc=1000.0, scale=20.0, size=n)
    y = rng.normal(loc=1000.0, scale=20.0, size=n)
    energy = rng.uniform(0.3, 3.0, size=n) * 1000.0

    table = Table({"X": x, "Y": y, "ENERGY": energy})
    hdu = fits.BinTableHDU(table)
    hdu.header["CDELT1"] = -1.0 / 3600.0
    hdu.header["CDELT2"] = 1.0 / 3600.0
    hdu.header["CRPIX1"] = 1.0
    hdu.header["CRPIX2"] = 1.0
    hdu.header["CRVAL1"] = 0.0
    hdu.header["CRVAL2"] = 0.0
    hdu.header["CTYPE1"] = "RA---TAN"
    hdu.header["CTYPE2"] = "DEC--TAN"
    evt_path = obs_dir / "test_evt2.fits"
    hdu.writeto(evt_path)

    outdir = tmp_path / "gas_proxy"
    result = build_gas_proxy(tmp_path, outdir)
    gas_path = outdir / "gas_counts.fits"
    report_path = outdir / "BUILD_REPORT.json"
    cert_path = outdir / "nis_gas_proxy_certificate.json"

    assert gas_path.exists()
    assert report_path.exists()
    assert cert_path.exists()

    report = json.loads(report_path.read_text())
    assert report["outputs"]["gas_counts_sha256"]
    cert = json.loads(cert_path.read_text())
    assert cert["output_digest"]
    assert result["certificate"]["output_digest"] == cert["output_digest"]
