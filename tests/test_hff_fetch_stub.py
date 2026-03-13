import json
from pathlib import Path

from tools.fetch_hff_lensmodel import build_provenance, select_best_maps


def test_select_best_maps_by_z(tmp_path):
    files = []
    for name in [
        "kappa_z7.fits",
        "kappa_z9.fits",
        "gamma1_z9.fits",
        "gamma2_z9.fits",
        "gamma1_z7.fits",
        "gamma2_z7.fits",
    ]:
        path = tmp_path / name
        path.write_text("fake")
        files.append(path)

    selected = select_best_maps(files)
    assert selected["kappa"].name == "kappa_z9.fits"
    assert selected["gamma1"].name == "gamma1_z9.fits"
    assert selected["gamma2"].name == "gamma2_z9.fits"


def test_build_provenance_schema(tmp_path):
    archive = tmp_path / "archive.tar.gz"
    archive.write_text("fake")
    selected = {"kappa": None, "gamma1": None, "gamma2": None}
    prov = build_provenance("A2744", "CATS", "http://example", archive, selected)
    assert prov["cluster"] == "A2744"
    assert prov["model"] == "CATS"
    assert "file_hashes" in prov
    assert "stable_provenance_hash" in prov
