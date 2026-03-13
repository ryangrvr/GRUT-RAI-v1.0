from __future__ import annotations

import argparse
import json
import re
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.utils import stable_sha256
from grut.cluster_packet import file_sha256


HFF_CLUSTERS = {"A2744", "MACS0416", "MACS0717", "MACS1149", "A370", "AS1063"}
HFF_MODELS = {"CATS", "Sharon", "Zitrin", "GLAFIC", "Diego", "Keeton"}

HFF_URLS: Dict[Tuple[str, str], str] = {
    # NOTE: URLs may evolve; override with --url if needed.
    ("A2744", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/abell2744/cats/",
    ("A2744", "Diego"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/abell2744/diego/",
    ("MACS0416", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/macs0416/cats/",
    ("MACS0717", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/macs0717/cats/",
    ("MACS1149", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/macs1149/cats/",
    ("A370", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/abell370/cats/",
    ("AS1063", "CATS"): "https://archive.stsci.edu/pub/hlsp/frontier-lens-models/as1063/cats/",
}

HFF_DIRECT_FILES: Dict[Tuple[str, str, str], Dict[str, str]] = {
    (
        "A2744",
        "CATS",
        "4.1",
    ): {
        "kappa": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/cats/v4.1/hlsp_frontier_model_abell2744_cats_v4.1_kappa.fits",
        "gamma": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/cats/v4.1/hlsp_frontier_model_abell2744_cats_v4.1_gamma.fits",
    },
    (
        "A2744",
        "CATS",
        "4",
    ): {
        "kappa": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/cats/v4/hlsp_frontier_model_abell2744_cats_v4_kappa.fits",
        "gamma": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/cats/v4/hlsp_frontier_model_abell2744_cats_v4_gamma.fits",
    },
    (
        "A2744",
        "GLAFIC",
        "4",
    ): {
        "kappa": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/glafic/v4/hlsp_frontier_model_abell2744_glafic_v4_kappa.fits",
        "gamma": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/glafic/v4/hlsp_frontier_model_abell2744_glafic_v4_gamma.fits",
    },
    (
        "A2744",
        "Sharon",
        "4cor",
    ): {
        "kappa": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/sharon/v4cor/hlsp_frontier_model_abell2744_sharon_v4cor_kappa.fits",
        "gamma": "https://archive.stsci.edu/pub/hlsp/frontier/abell2744/models/sharon/v4cor/hlsp_frontier_model_abell2744_sharon_v4cor_gamma.fits",
    },
}


def _download(url: str, dest: Path) -> None:
    with urlopen(url) as response:
        data = response.read()
    dest.write_bytes(data)


def _extract(archive_path: Path, extract_dir: Path) -> None:
    extract_dir.mkdir(parents=True, exist_ok=True)
    if archive_path.suffix in {".zip"}:
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(extract_dir)
        return
    if archive_path.suffixes[-2:] == [".tar", ".gz"] or archive_path.suffix == ".tgz":
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(extract_dir)
        return
    raise ValueError("Unsupported archive format; expected .zip or .tar.gz")


def _find_fits_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.fits") if p.is_file()]


def _parse_z_from_name(name: str) -> Optional[float]:
    match = re.search(r"z(?:=)?([0-9]+(?:\.[0-9]+)?)", name, re.IGNORECASE)
    if not match:
        return None
    return float(match.group(1))


def _select_by_kind(files: List[Path], kind: str) -> List[Path]:
    kind = kind.lower()
    if kind == "kappa":
        return [p for p in files if re.search(r"kappa|kap", p.name, re.IGNORECASE)]
    if kind == "gamma1":
        return [p for p in files if re.search(r"gamma1|g1", p.name, re.IGNORECASE)]
    if kind == "gamma2":
        return [p for p in files if re.search(r"gamma2|g2", p.name, re.IGNORECASE)]
    return []


def select_best_maps(files: List[Path]) -> Dict[str, Optional[Path]]:
    candidates = {
        "kappa": _select_by_kind(files, "kappa"),
        "gamma1": _select_by_kind(files, "gamma1"),
        "gamma2": _select_by_kind(files, "gamma2"),
    }

    def by_z(paths: List[Path]) -> Dict[float, Path]:
        out: Dict[float, Path] = {}
        for p in paths:
            z = _parse_z_from_name(p.name)
            if z is None:
                continue
            out[z] = p
        return out

    z_maps = {k: by_z(v) for k, v in candidates.items()}
    z_common = set(z_maps["kappa"]) & set(z_maps["gamma1"]) & set(z_maps["gamma2"])
    selected: Dict[str, Optional[Path]] = {"kappa": None, "gamma1": None, "gamma2": None}

    if z_common:
        z_pick = max(z_common)
        selected["kappa"] = z_maps["kappa"][z_pick]
        selected["gamma1"] = z_maps["gamma1"][z_pick]
        selected["gamma2"] = z_maps["gamma2"][z_pick]
        return selected

    for kind, files_list in candidates.items():
        if not files_list:
            continue
        with_z = [(p, _parse_z_from_name(p.name)) for p in files_list]
        with_z_sorted = sorted(with_z, key=lambda t: (t[1] is None, t[1] or -1), reverse=True)
        selected[kind] = with_z_sorted[0][0]

    return selected


def build_provenance(
    cluster: str,
    model: str,
    source_url: Optional[str],
    archive_path: Optional[Path],
    selected: Dict[str, Optional[Path]],
    file_urls: Optional[Dict[str, str]] = None,
) -> Dict[str, object]:
    files_hashes = {
        "archive": file_sha256(str(archive_path)) if archive_path and archive_path.exists() else None,
    }
    if file_urls:
        for key, url in file_urls.items():
            files_hashes[key] = file_sha256(str(selected.get(key))) if selected.get(key) else None
    selected_names = {k: (v.name if v is not None else None) for k, v in selected.items()}
    provenance = {
        "cluster": cluster,
        "model": model,
        "source_url": source_url,
        "file_urls": file_urls,
        "download_timestamp": datetime.now(timezone.utc).isoformat(),
        "file_hashes": files_hashes,
        "selected_maps": selected_names,
    }
    stable_prov = dict(provenance)
    stable_prov.pop("download_timestamp", None)
    provenance["stable_provenance_hash"] = stable_sha256(stable_prov)
    return provenance


def fetch_hff_lensmodel(
    cluster: str,
    model: str,
    outdir: Path,
    url_override: Optional[str] = None,
    archive_name: Optional[str] = None,
    version: Optional[str] = None,
) -> Dict[str, object]:
    cluster = cluster.upper()
    model = model
    if cluster not in HFF_CLUSTERS:
        raise ValueError(f"Unknown cluster: {cluster}")
    if model not in HFF_MODELS:
        raise ValueError(f"Unknown model: {model}")

    outdir.mkdir(parents=True, exist_ok=True)
    raw_dir = outdir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    extract_dir = outdir / "extracted"
    extract_dir.mkdir(parents=True, exist_ok=True)
    selected_dir = outdir / "selected"
    selected_dir.mkdir(parents=True, exist_ok=True)

    if cluster == "A2744" and model in {"CATS", "GLAFIC", "Sharon"}:
        if model == "CATS":
            versions = [version] if version else ["4.1", "4"]
        elif model == "Sharon":
            versions = [version] if version else ["4cor", "4"]
        else:
            versions = [version] if version else ["4"]
        file_urls = None
        for ver in versions:
            file_urls = HFF_DIRECT_FILES.get((cluster, model, ver))
            if file_urls:
                break
        if file_urls:
            provenance_path = outdir / "PROVENANCE.json"
            if provenance_path.exists():
                try:
                    existing = json.loads(provenance_path.read_text())
                    stable_hash = existing.get("stable_provenance_hash")
                    if stable_hash:
                        return existing
                except Exception:
                    pass

            selected: Dict[str, Optional[Path]] = {}
            for key, url in file_urls.items():
                target = selected_dir / f"{key}.fits"
                if not target.exists():
                    _download(url, target)
                selected[key] = target

            provenance = build_provenance(
                cluster,
                model,
                source_url=None,
                archive_path=None,
                selected=selected,
                file_urls=file_urls,
            )
            (outdir / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2))
            return provenance

    source_url = url_override or HFF_URLS.get((cluster, model))
    if not source_url:
        raise ValueError("No URL mapping found; use --url to provide a direct archive URL")

    if not archive_name:
        archive_name = f"{cluster.lower()}_{model.lower()}_lensmodel.tar.gz"

    archive_path = raw_dir / archive_name
    provenance_path = outdir / "PROVENANCE.json"
    if archive_path.exists() and provenance_path.exists():
        try:
            existing = json.loads(provenance_path.read_text())
            expected_hash = existing.get("file_hashes", {}).get("archive")
            if expected_hash and expected_hash == file_sha256(str(archive_path)):
                return existing
        except Exception:
            pass

    if not archive_path.exists():
        _download(source_url, archive_path)

    _extract(archive_path, extract_dir)
    fits_files = _find_fits_files(extract_dir)
    selected = select_best_maps(fits_files)

    for kind, path in selected.items():
        if path is None:
            continue
        target = selected_dir / f"{kind}.fits"
        target.write_bytes(path.read_bytes())

    provenance = build_provenance(cluster, model, source_url, archive_path, selected)
    (outdir / "PROVENANCE.json").write_text(json.dumps(provenance, indent=2))
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch HFF lens model FITS maps")
    parser.add_argument("--cluster", default="A2744")
    parser.add_argument("--model", default="CATS")
    parser.add_argument("--outdir", default="artifacts/hff_raw")
    parser.add_argument("--url", default=None)
    parser.add_argument("--archive_name", default=None)
    parser.add_argument("--version", default=None)
    args = parser.parse_args()

    outdir = Path(args.outdir) / args.cluster / args.model
    fetch_hff_lensmodel(
        cluster=args.cluster,
        model=args.model,
        outdir=outdir,
        url_override=args.url,
        archive_name=args.archive_name,
        version=args.version,
    )


if __name__ == "__main__":
    main()
