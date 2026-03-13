# Quantum Bridge Appendix Final (Tier B)

## Scope
This appendix documents the **Tier B** derivation context for the quantum boundary operator while deferring all operational claims to Tier A evidence packets.

**Authoritative outputs**: The evidence packet built by the code in tools/build_quantum_evidence_packet.py and its NIS certificate. If any statement here conflicts with that packet, **flag the conflict**.

## Operator Anchor
- Operator: OP_QUANTUM_DECOHERE_001
- Controlled policy: uses fixed $\omega$ input (experimental interface)
- Self-consistent policy: uses cubic closure and emits the emergent scaling

## Expected Scaling (Tier B Summary)
- Self-consistent closure yields the emergent $m^{-2/3}$ scaling.
- Controlled policy yields the inherited $m^{-2}$ scaling (DP reference).

**Note:** The numerical values, fit methods, and slopes are defined by the evidence packet outputs and must not be re-stated here if they diverge.

## Evidence Packet Authority
Operational evidence lives in the quantum evidence packet:
- Builder: tools/build_quantum_evidence_packet.py
- Outputs: artifacts/evidence_quantum_v0_1/
- Certificate: nis_quantum_certificate.json
- Summary: summary.csv (slopes and fit metadata)

## Conflict Policy
If this appendix and the evidence packet differ:
1. Flag the conflict.
2. Defer to the evidence packet and NIS certificate.
3. Do not adjust prose to match silently.
