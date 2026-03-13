import json
import numpy as np

from tools.register_gas_to_kappa import register_gas_to_kappa

try:
    from astropy.io import fits  # type: ignore
except Exception:  # pragma: no cover
    fits = None


def _write_fits(path, data, header):
    hdu = fits.PrimaryHDU(data=data, header=header)
    hdu.writeto(path, overwrite=True)


def test_register_gas_to_kappa(tmp_path):
    if fits is None:
        return

    n = 32
    y, x = np.indices((n, n))
    kappa = np.exp(-((x - 16) ** 2 + (y - 16) ** 2) / (2.0 * 4.0**2))
    gas = np.exp(-((x - 18) ** 2 + (y - 14) ** 2) / (2.0 * 4.0**2))

    header = fits.Header()
    header["CRPIX1"] = 1.0
    header["CRPIX2"] = 1.0
    header["CRVAL1"] = 0.0
    header["CRVAL2"] = 0.0
    header["CDELT1"] = -1.0 / 3600.0
    header["CDELT2"] = 1.0 / 3600.0
    header["CTYPE1"] = "RA---TAN"
    header["CTYPE2"] = "DEC--TAN"

    kappa_path = tmp_path / "kappa.fits"
    gas_path = tmp_path / "gas.fits"
    _write_fits(kappa_path, kappa, header)
    _write_fits(gas_path, gas, header)

    outdir = tmp_path / "reg"
    report = register_gas_to_kappa(kappa_path, gas_path, outdir)
    registered = np.load(outdir / "gas_registered.npy")

    ky, kx = np.unravel_index(np.argmax(kappa), kappa.shape)
    gy, gx = np.unravel_index(np.argmax(registered), registered.shape)
    assert abs(kx - gx) <= 2
    assert abs(ky - gy) <= 2

    report_path = outdir / "registration_report.json"
    assert report_path.exists()
    data = json.loads(report_path.read_text())
    assert data["method"]
    assert data["registration_hash"]
