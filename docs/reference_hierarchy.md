# GRUT Canonical Reference Hierarchy

This document defines the authority order for resolving conflicts between prose and operational artifacts. **Do not auto-resolve conflicts. Flag them.**

## Authority Order (Highest → Lowest)
1. **Code + Evidence Packets + NIS Certificates**
   - Source of truth for operational claims and emitted observables.
   - Deterministic outputs with hashes are authoritative.
2. **Canonical Appendices / Operator Specs**
   - Tier B derivations and specifications.
   - Must not override Tier A evidence if discrepancies exist.
3. **ToE Overview PDF**
   - High-level synthesis only. No operational authority.

## Conflict-Flagging Protocol
When prose conflicts with code/evidence:
- **Flag the conflict** in writing rather than harmonizing silently.
- State which artifact is authoritative (Tier A evidence/certificates) and which prose statement is in conflict.
- Add a short note in the relevant appendix or spec indicating the mismatch.

## Current Canonical Documents (Expected Locations)
- Code + Evidence Packets + NIS Certificates: codebase and artifacts
- Canonical Appendices / Operator Specs:
  - Quantum Bridge Appendix Final: docs/quantum_bridge_appendix_final.md
  - 3-Loop / Anomaly Appendix: docs/three_loop_anomaly_appendix.md
  - Particle Bridge Spec v0.1: docs/particle_bridge_spec_v0_1.md
  - Canon Status Note: docs/canon_status_note.md
- ToE Overview PDF:
   - docs/toe_overview_canonical.pdf

## Important Caution
The ToE PDF must **not** substitute for code, evidence packets, or NIS certificates. The authority order above is mandatory.
