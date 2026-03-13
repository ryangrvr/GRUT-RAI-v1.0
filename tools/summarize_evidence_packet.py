from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.audit_schemas import Phase2EvidencePacket


def summarize_evidence_packet(*, packet_path: str, outdir: str) -> str:
    packet = json.loads(Path(packet_path).read_text())
    Phase2EvidencePacket.model_validate(packet)

    out_path = Path(outdir)
    out_path.mkdir(parents=True, exist_ok=True)
    summary_path = out_path / "summary_table.csv"

    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["component", "path", "sha256", "kind", "size_bytes"],
        )
        writer.writeheader()
        for comp in packet.get("components", []):
            writer.writerow(
                {
                    "component": comp.get("name"),
                    "path": comp.get("path"),
                    "sha256": comp.get("sha256"),
                    "kind": comp.get("kind"),
                    "size_bytes": comp.get("size_bytes"),
                }
            )
    return str(summary_path)


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize Phase-2 evidence packet")
    parser.add_argument(
        "--packet",
        default="artifacts/evidence_packet_phase2_cosmo_v0/phase2_evidence_packet.json",
    )
    parser.add_argument("--outdir", default="artifacts/evidence_packet_phase2_cosmo_v0")
    args = parser.parse_args()

    summarize_evidence_packet(packet_path=args.packet, outdir=args.outdir)


if __name__ == "__main__":
    main()