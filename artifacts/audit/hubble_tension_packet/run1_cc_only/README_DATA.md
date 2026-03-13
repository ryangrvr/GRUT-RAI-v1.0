# Hubble Tension Evidence Packet v0.2.1

This Tier A packet compares GRUT cosmology outputs to a fixed ΛCDM reference and to an offline H(z) compilation.

## Presets
- matter_only
- vacuum_plus_matter (domain-of-validity gating if valid_z_max is set)

## Anchor Policy
E(z) = H(z)/H(0) is the anchor-free shape observable.
Anchored H(z) uses explicit anchors with no fitting:
- Planck_67p4: H0 = 67.4 km/s/Mpc
- SH0ES_73p0: H0 = 73.0 km/s/Mpc

H(z) scaling policy: Hz_phys(z) = Hz_code(z) * (H0_phys / H0_code).

## Shape-Only Residuals
E(z) residuals are computed using a dataset anchor policy (lowest_z or median_lowz).
These provide an anchor-free shape comparison with tracer-split reporting.

## Dataset Policy
Dataset curation is explicit via --dataset_policy: min, cc_only, bao_only, all.

## ΛCDM Reference (No Fitting)
Reference parameters are fixed and logged: Ωm=0.315, ΩΛ=0.685, Ωk=0, Ωr=0.

## Claims / Non-Claims
This packet emits residual metrics only. It does not fit or tune model parameters.
Network access is not used in tests or audit; data are bundled offline.

## Reproduction
python tools/build_hubble_tension_packet.py --outdir artifacts/evidence_hubble_tension_v0_2_1
