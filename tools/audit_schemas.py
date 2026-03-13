from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class AnchorPolicy(BaseModel):
    name: str
    H0_km_s_Mpc: float
    scale_H: float


class CalibrationManifest(BaseModel):
    preset: str
    alpha_mem: float
    start_z: float
    dt_years: float
    steps: int
    canon_hash: Optional[str] = None
    repro_hash: Optional[str] = None
    output_digest: Optional[str] = None
    H0_code: Optional[float] = None
    idx0: Optional[int] = None
    z0: Optional[float] = None
    status: str
    failure_reason: Optional[str] = None
    anchors: List[AnchorPolicy]
    sigma8_0: float
    compare_definition: Optional[str] = None
    valid_z_max: Optional[float] = None


class SweepRunConfig(BaseModel):
    dt_years: float
    steps: int
    integrator: str
    start_z: float
    rho_is_rho0: bool


class SweepSpec(BaseModel):
    param: str
    grid: List[float]
    run_config: SweepRunConfig
    init_state: Dict[str, Any]
    valid_z_max: Optional[float] = None
    canon: str


class SweepManifest(BaseModel):
    sweep: SweepSpec
    run_folders: List[str]


class QuantumBoundaryPacket(BaseModel):
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    constants: Dict[str, Any]


class EvidencePacketComponent(BaseModel):
    name: str
    path: str
    sha256: str
    kind: str
    size_bytes: int


class Phase2EvidencePacket(BaseModel):
    schema: str
    created_at: str
    components: List[EvidencePacketComponent]
    notes: Optional[str] = None