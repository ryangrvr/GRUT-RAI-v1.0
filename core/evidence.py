"""Evidence packet schema and builders."""

import json
import hashlib
import uuid
from datetime import datetime
from typing import Dict, Any, Optional


def make_canonical_json(obj: Any) -> str:
    """Produce canonical JSON with sorted keys for hashing."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def make_evidence_packet(
    kind: str,
    request: Dict[str, Any],
    response: Dict[str, Any],
    engine_version: str,
    params_hash: str,
    receipt: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build an evidence packet (exportable/publishable bundle).

    The packet follows schema `grut-evidence-v1` and contains a `header` with
    stable identifying fields and a `bundle_hash` computed deterministically
    from the header (without bundle_hash), request, and receipt.
    """
    created_at = datetime.utcnow().isoformat()

    # Extract receipt from response if not provided
    if receipt is None:
        if "nis" in response:
            receipt = response["nis"]
        elif "ris" in response:
            receipt = response["ris"]
        else:
            receipt = {}

    status = receipt.get("status") if isinstance(receipt, dict) else None

    header = {
        "id": str(uuid.uuid4()),
        "kind": kind,
        "created_at": created_at,
        "engine_version": engine_version,
        "params_hash": params_hash,
        "status": status,
        # bundle_hash filled below
    }

    packet = {
        "schema": "grut-evidence-v1",
        "header": header,
        "request": request,
        "response": response,
        "receipt": receipt,
    }

    # Compute bundle hash from canonical JSON of header (without bundle_hash) + request + receipt
    bundle_input = {
        "header": header,
        "request": request,
        "receipt": receipt,
    }
    canonical_json = make_canonical_json(bundle_input)
    bundle_hash = hashlib.sha256(canonical_json.encode()).hexdigest()

    packet["header"]["bundle_hash"] = bundle_hash

    # Backwards compatible fields
    packet["metadata"] = {
        "kind": kind,
        "created_at": created_at,
        "engine_version": engine_version,
        "params_hash": params_hash,
    }
    packet["bundle_hash"] = bundle_hash

    return packet


def verify_evidence_packet(packet: Dict[str, Any]) -> bool:
    """Verify integrity of evidence packet.

    This supports both the legacy format (metadata + bundle_hash at top-level)
    and the new header-based format.
    """
    # Prefer header-based verification
    if packet.get("header"):
        header = dict(packet.get("header", {}))
        # Remove bundle_hash if present for verification input
        header.pop("bundle_hash", None)
        bundle_data = {
            "header": header,
            "request": packet.get("request", {}),
            "receipt": packet.get("receipt", {}),
        }
    else:
        bundle_data = {
            "metadata": packet.get("metadata", {}),
            "request": packet.get("request", {}),
            "receipt": packet.get("receipt", {}),
        }

    canonical_json = make_canonical_json(bundle_data)
    computed_hash = hashlib.sha256(canonical_json.encode()).hexdigest()

    expected_hash = packet.get("bundle_hash") or (packet.get("header") or {}).get("bundle_hash")
    if not expected_hash:
        return False

    return expected_hash == computed_hash
