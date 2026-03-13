# Quantum Evidence Packet v0.1

This packet provides deterministic, Tier A quantum decoherence benchmarks and scans for the $m^{-2/3}$ bridge.

Claims:
- Controlled $\omega$ oracle and self-consistent closure.
- Slope falsifier (log-log mass scans) with explicit policy split.

Not claimed:
- No Tier B constants (no 3-loop residue, no r_sat).
- No particle-sector predictions.

Units:
- $\omega$ in rad_per_s
- l in m
- m in kg

Commands:
- python tools/build_quantum_evidence_packet.py --outdir artifacts/evidence_quantum_v0_1
