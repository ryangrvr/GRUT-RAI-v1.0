#!/usr/bin/env python3
"""Build a deterministic release bundle for Zenodo upload.

Selects evidence packets by pattern, copies them into a release_bundle/
directory with public-facing normalized paths, writes a RELEASE_INDEX.json
with combined digest, and includes the ToE PDF + appendices.

Bundle paths are human-legible and stable:
    packets/hubble_tension/run1
    packets/quantum_evidence/run1
    packets/rotation/packet_galaxy
    packets/cluster_hff_v0_6A/A2744/CATS

Usage:
    python tools/build_release_bundle.py \
        --patterns "evidence_*" "audit/hubble_tension_packet" \
        --no-audit \
        --outdir artifacts/release_bundle_v0_1

    python tools/build_release_bundle.py \
        --all \
        --outdir artifacts/release_bundle_v0_1
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
DOCS_DIR = PROJECT_ROOT / "docs"

# Standard documents to include in every release.
# Maps source path (relative to PROJECT_ROOT) -> public filename in bundle.
RELEASE_DOCS: Dict[str, str] = {
    "docs/toe_overview_canonical.pdf": "GRUT_Theory_of_Everything_upload_ready.pdf",
    "docs/quantum_bridge_appendix_final.md": "quantum_bridge_appendix_final.md",
    "docs/three_loop_anomaly_appendix.md": "three_loop_anomaly_appendix.md",
    "docs/particle_bridge_spec_v0_1.md": "particle_bridge_spec_v0_1.md",
    "docs/reference_hierarchy.md": "reference_hierarchy.md",
    "docs/canon_status_note.md": "canon_status_note.md",
}


# ── Path normalization rules ────────────────────────────────────────────
# Each rule is (prefix_to_match, replacement_prefix, join_char).
# Rules are tried in order; first match wins.
# "join_char" is used to flatten remaining subpath segments when the
# original nesting is too deep (e.g. rotation_packet/packet/galaxy ->
# rotation/packet_galaxy).

_BUNDLE_PATH_RULES: List[Tuple[str, str, str | None]] = [
    # audit/hubble_tension_packet/<run> -> hubble_tension/<run>
    ("audit/hubble_tension_packet/", "hubble_tension/", None),
    # audit/quantum_evidence_packet/<run> -> quantum_evidence/<run>
    ("audit/quantum_evidence_packet/", "quantum_evidence/", None),
    # audit/rotation_packet/packet/<name> -> rotation/packet_<name>
    ("audit/rotation_packet/packet/", "rotation/packet_", "_"),
    # audit/rotation_batch/batch/<name> -> rotation/batch_<name>
    ("audit/rotation_batch/batch/", "rotation/batch_", "_"),
    # evidence_cluster_v0_6A/<cluster>/<model>/outputs/profile_packet
    #   -> cluster_hff_v0_6A/<cluster>/<model>/profile_packet
    # (handled by strip-outputs rule below after prefix swap)
    ("evidence_cluster_v0_6A/", "cluster_hff_v0_6A/", None),
    ("evidence_cluster_v0_6A_batch/", "cluster_hff_v0_6A_batch/", None),
]


def normalize_bundle_path(source_path: str) -> str:
    """Convert an internal artifact path to a public-facing bundle path.

    Examples
    -------
    artifacts/audit/hubble_tension_packet/run1
        -> packets/hubble_tension/run1
    artifacts/audit/quantum_evidence_packet/run1
        -> packets/quantum_evidence/run1
    artifacts/audit/rotation_packet/packet/galaxy
        -> packets/rotation/packet_galaxy
    artifacts/audit/rotation_batch/batch/g1
        -> packets/rotation/batch_g1
    artifacts/evidence_cluster_v0_6A/A2744/CATS
        -> packets/cluster_hff_v0_6A/A2744/CATS
    artifacts/evidence_cluster_v0_6A/A2744/CATS/outputs/profile_packet
        -> packets/cluster_hff_v0_6A/A2744/CATS/profile_packet
    """
    # Strip leading artifacts/ prefix
    p = source_path
    if p.startswith("artifacts/"):
        p = p[len("artifacts/"):]

    for prefix, replacement, join_char in _BUNDLE_PATH_RULES:
        if p.startswith(prefix):
            rest = p[len(prefix):]
            if join_char is not None:
                # Flatten remaining subpath segments with join_char
                rest = join_char.join(rest.split("/"))
            result = replacement + rest
            # Clean up /outputs/profile_packet -> /profile_packet
            result = result.replace("/outputs/profile_packet", "/profile_packet")
            return f"packets/{result}"

    # Fallback: flatten entire path with underscores
    return f"packets/{p.replace('/', '_')}"


# ── Hashing helpers ─────────────────────────────────────────────────────


def sha256_file(path: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_str(s: str) -> str:
    """SHA-256 of a string."""
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ── Packet discovery ────────────────────────────────────────────────────


def discover_packets(
    patterns: List[str],
    include_audit: bool = True,
) -> List[Path]:
    """Discover packet directories matching the given patterns.

    A directory is considered a packet if it contains PACKET_INDEX.json
    or an nis_*certificate*.json file.
    """
    candidates: set = set()

    for pattern in patterns:
        for p in ARTIFACTS_DIR.glob(pattern):
            if p.is_dir():
                candidates.add(p)

    if include_audit:
        audit_dir = ARTIFACTS_DIR / "audit"
        if audit_dir.exists():
            for d in audit_dir.iterdir():
                if d.is_dir():
                    candidates.add(d)

    # For each candidate, find actual packet dirs (those with index or cert)
    packet_dirs: set = set()
    for cand in sorted(candidates):
        # Check if this dir itself is a packet
        has_idx = list(cand.glob("PACKET_INDEX.json"))
        has_cert = list(cand.glob("nis_*certificate*.json"))
        if has_idx or has_cert:
            packet_dirs.add(cand)

        # Also check subdirs (max depth 5)
        for sub_idx in cand.rglob("PACKET_INDEX.json"):
            try:
                rel = sub_idx.relative_to(cand)
                if len(rel.parts) <= 6:
                    packet_dirs.add(sub_idx.parent)
            except ValueError:
                continue

        for sub_cert in cand.rglob("nis_*certificate*.json"):
            try:
                rel = sub_cert.relative_to(cand)
                if len(rel.parts) <= 6:
                    # Only add if no PACKET_INDEX already covers this dir
                    pdir = sub_cert.parent
                    if not (pdir / "PACKET_INDEX.json").exists():
                        packet_dirs.add(pdir)
            except ValueError:
                continue

    return sorted(packet_dirs)


# ── File copying ────────────────────────────────────────────────────────


def copy_packet(src_dir: Path, dst_dir: Path) -> Dict[str, str]:
    """Copy a packet directory and return file hashes."""
    file_hashes: Dict[str, str] = {}

    for src_file in sorted(src_dir.rglob("*")):
        if not src_file.is_file():
            continue

        rel = src_file.relative_to(src_dir)
        dst_file = dst_dir / rel
        dst_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_file, dst_file)
        file_hashes[str(rel)] = sha256_file(dst_file)

    return file_hashes


# ── Index construction ──────────────────────────────────────────────────


def build_release_index(
    outdir: Path,
    packet_entries: List[Dict[str, Any]],
    doc_hashes: Dict[str, str],
) -> Dict[str, Any]:
    """Build the RELEASE_INDEX.json content."""
    # Combined digest: hash all output_digests + doc hashes in sorted order.
    # Sort packets by source_path for determinism.
    digest_parts = []
    for entry in sorted(packet_entries, key=lambda e: e["source_path"]):
        od = entry.get("output_digest", "")
        if od:
            digest_parts.append(od)
    for doc_name in sorted(doc_hashes.keys()):
        digest_parts.append(doc_hashes[doc_name])

    combined_digest = sha256_str("|".join(digest_parts))

    return {
        "release_version": outdir.name,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "combined_digest": combined_digest,
        "packet_count": len(packet_entries),
        "doc_count": len(doc_hashes),
        "packets": packet_entries,
        "docs": doc_hashes,
    }


# ── Main ────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Build GRUT-RAI release bundle")
    parser.add_argument(
        "--patterns",
        nargs="+",
        default=["evidence_*"],
        help="Glob patterns for artifact directories (default: evidence_*)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Include all discoverable evidence families",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=ARTIFACTS_DIR / "release_bundle_v0_1",
        help="Output directory (default: artifacts/release_bundle_v0_1)",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Exclude audit/ subdirectories",
    )
    parser.add_argument(
        "--no-docs",
        action="store_true",
        help="Exclude ToE PDF and appendices",
    )
    args = parser.parse_args()

    if args.all:
        patterns = [
            "evidence_*",
            "_audit_*",
            "*_packet_*",
            "*_batch_*",
            "cluster_prediction_*",
            "cluster_sample",
            "quantum_boundary*",
            "lensing_packet_*",
        ]
    else:
        patterns = args.patterns

    outdir = args.outdir
    if outdir.exists():
        print(f"ERROR: Output directory already exists: {outdir}", file=sys.stderr)
        print("Remove it first or choose a different --outdir.", file=sys.stderr)
        sys.exit(1)

    outdir.mkdir(parents=True)
    packets_dir = outdir / "packets"
    packets_dir.mkdir()

    # ── Discover packets ──
    print(f"Discovering packets with patterns: {patterns}")
    packet_dirs = discover_packets(patterns, include_audit=not args.no_audit)
    print(f"Found {len(packet_dirs)} packet directories")

    # ── Check for bundle_path collisions ──
    seen_bundle_paths: Dict[str, str] = {}
    pre_entries: List[Tuple[Path, str, str]] = []
    for pdir in packet_dirs:
        source_path = str(pdir.relative_to(PROJECT_ROOT))
        bundle_path = normalize_bundle_path(source_path)
        if bundle_path in seen_bundle_paths:
            print(
                f"  WARNING: bundle_path collision: {bundle_path}\n"
                f"    from {source_path}\n"
                f"    and  {seen_bundle_paths[bundle_path]}",
                file=sys.stderr,
            )
        seen_bundle_paths[bundle_path] = source_path
        pre_entries.append((pdir, source_path, bundle_path))

    # ── Copy packets ──
    packet_entries: List[Dict[str, Any]] = []
    for pdir, source_path, bundle_path in pre_entries:
        # Use bundle_path as the on-disk directory (relative to outdir)
        dst = outdir / bundle_path

        print(f"  Copying {source_path}")
        print(f"       -> {bundle_path}")
        file_hashes = copy_packet(pdir, dst)

        # Read PACKET_INDEX.json if present
        idx_path = pdir / "PACKET_INDEX.json"
        idx_data: Dict[str, Any] = {}
        if idx_path.exists():
            idx_data = json.loads(idx_path.read_text())

        # Find NIS certificate for tool_version
        tool_version = ""
        input_hash = idx_data.get("input_hash", "")
        output_digest = idx_data.get("output_digest", "")

        cert_info = idx_data.get("profile_packet_certificate", {})
        if not cert_info:
            cert_info = idx_data.get("certificate", {})
            if isinstance(cert_info, dict) and "certificate" in cert_info:
                cert_info = cert_info["certificate"]

        for nis_path in sorted(pdir.rglob("nis_*certificate*.json")):
            try:
                nis_data = json.loads(nis_path.read_text())
                if not tool_version:
                    tool_version = nis_data.get("tool_version", "")
                if not input_hash:
                    input_hash = nis_data.get("input_hash", "")
                if not output_digest:
                    output_digest = nis_data.get("output_digest", "")
                break
            except Exception:
                continue

        if not tool_version:
            tool_version = cert_info.get("tool_version", "")
        if not input_hash:
            input_hash = cert_info.get("input_hash", "")
        if not output_digest:
            output_digest = cert_info.get("output_digest", "")

        packet_entries.append({
            "source_path": source_path,
            "bundle_path": bundle_path,
            "tool_version": tool_version,
            "input_hash": input_hash,
            "output_digest": output_digest,
            "canon_hash": idx_data.get("canon_hash", "") or "",
            "file_count": len(file_hashes),
            "file_hashes": file_hashes,
        })

    # ── Copy docs ──
    doc_hashes: Dict[str, str] = {}
    if not args.no_docs:
        docs_out = outdir / "docs"
        docs_out.mkdir()
        for doc_srcpath, doc_pubname in RELEASE_DOCS.items():
            src = PROJECT_ROOT / doc_srcpath
            if src.exists():
                dst = docs_out / doc_pubname
                shutil.copy2(src, dst)
                doc_hashes[doc_pubname] = sha256_file(dst)
                print(f"  Doc: {doc_srcpath} -> docs/{doc_pubname}")
            else:
                print(f"  WARNING: Doc not found: {doc_srcpath}")

    # ── Build RELEASE_INDEX.json ──
    release_index = build_release_index(outdir, packet_entries, doc_hashes)
    index_path = outdir / "RELEASE_INDEX.json"
    index_path.write_text(json.dumps(release_index, indent=2, default=str))

    print()
    print(f"Release bundle written to: {outdir}")
    print(f"  Packets:         {len(packet_entries)}")
    print(f"  Docs:            {len(doc_hashes)}")
    print(f"  Combined digest: {release_index['combined_digest']}")
    print(f"  Index:           {index_path}")

    return release_index


if __name__ == "__main__":
    main()
