from __future__ import annotations

import json
from pathlib import Path


def test_particle_bridge_spec_files_exist() -> None:
    md_path = Path("docs/particle_bridge_spec_v0_1.md")
    json_path = Path("docs/particle_bridge_spec_v0_1.json")
    assert md_path.exists()
    assert json_path.exists()


def test_particle_bridge_spec_json_schema() -> None:
    payload = json.loads(Path("docs/particle_bridge_spec_v0_1.json").read_text())
    assert payload["tier"] == "B"
    ops = {op["id"] for op in payload["future_operators"]}
    required = {
        "OP_PARTICLE_LOCALIZATION_001",
        "OP_PARTICLE_MASS_SHIFT_001",
        "OP_G_MINUS_2_001",
        "OP_DECAY_CHANNEL_SHIFT_001",
        "OP_NEUTRINO_DECOHERE_001",
    }
    assert required.issubset(ops)
