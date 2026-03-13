from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from grut.utils import stable_sha256
from grut.cluster_packet import file_sha256


def _run_cmd(cmd: List[str]) -> None:
    result = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(cmd)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def fetch_chandra_obsids(obsids: List[str], outdir: Path) -> dict:
    outdir.mkdir(parents=True, exist_ok=True)
    tool = shutil.which("download_chandra_obsid")
    if not tool:
        raise RuntimeError(
            "download_chandra_obsid not found. Install CIAO and ensure it is on PATH, "
            "or manually download primary bundles into artifacts/chandra_raw/A2744/obsid_<id>/"
        )

    results = []
    for obsid in obsids:
        obs_dir = outdir / f"obsid_{obsid}"
        obs_dir.mkdir(parents=True, exist_ok=True)
        cmd = [tool, str(obsid), "--output", str(obs_dir)]
        _run_cmd(cmd)
        results.append({"obsid": obsid, "path": str(obs_dir), "command": cmd})

    hashes = {r["obsid"]: None for r in results}
    provenance = {
        "target": "A2744",
        "obsids": obsids,
        "tool": tool,
        "results": results,
        "hashes": hashes,
    }
    provenance["stable_provenance_hash"] = stable_sha256(
        {"target": provenance["target"], "obsids": obsids, "tool": tool}
    )
    (outdir / "CHANDRA_PROVENANCE.json").write_text(json.dumps(provenance, indent=2))
    return provenance


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch Chandra A2744 ObsIDs")
    parser.add_argument(
        "--obsids",
        default="2212,7712,7915,8477,8557",
    )
    parser.add_argument("--outdir", default="artifacts/chandra_raw/A2744")
    args = parser.parse_args()

    obsids = [o.strip() for o in args.obsids.split(",") if o.strip()]
    fetch_chandra_obsids(obsids, Path(args.outdir))


if __name__ == "__main__":
    main()
