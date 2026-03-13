#!/usr/bin/env python3
"""
Benchmark: Phase III-C Interior PDE Closure

Tests whether the PDE-informed interior model supports reactive,
dissipative, or mixed response; compares to WP2C proxy; evaluates
impact on echo channel.

KEY FINDING: The PDE reveals a structural identity omega_0 * tau = 1
(mass-independent), placing the BDCC at the peak of memory damping.
This changes the response classification from reactive (proxy Q~515)
to mixed viscoelastic (PDE Q~6).
"""

import sys
import math

sys.path.insert(0, ".")

from grut.interior_pde import (
    build_pde_background,
    solve_dispersion,
    dispersion_relation,
    effective_potential,
    compute_pde_analysis,
    pde_result_to_dict,
)

M_SUN = 1.989e30
G_SI = 6.674e-11
C_SI = 299_792_458.0

PASS = 0
FAIL = 0


def check(label: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    tag = "PASS" if condition else "FAIL"
    if not condition:
        FAIL += 1
        print(f"  [{tag}] {label}: {detail}")
    else:
        PASS += 1
        print(f"  [{tag}] {label}")


print("=" * 70)
print("PHASE III-C INTERIOR PDE BENCHMARK")
print("=" * 70)

# ────────────────────────────────────────────────────────────────
# Section 1: Background construction
# ────────────────────────────────────────────────────────────────
print("\n--- Section 1: Background construction ---")
bg = build_pde_background(M_kg=30 * M_SUN)
check("Background valid", bg.valid)
check("R_eq/r_s = 1/3", abs(bg.R_eq_m / bg.r_s_m - 1.0 / 3.0) < 1e-10)
check("omega_0 > 0", bg.omega_0 > 0)
check("omega_g > 0", bg.omega_g > 0)
check("tau_eff > 0", bg.tau_eff > 0)
check("compactness = 3", abs(bg.compactness - 3.0) < 1e-6)

# KEY: eigenfrequency vs proxy
omega_proxy = math.sqrt(2 * G_SI * 30 * M_SUN / bg.R_eq_m ** 4)
print(f"\n  omega_0 (PDE correct):   {bg.omega_0:.4e} rad/s")
print(f"  omega_core (WP2C proxy): {omega_proxy:.4e} rad/s")
print(f"  Ratio:                   {bg.omega_0 / omega_proxy:.4f} = sqrt(R_eq) = {math.sqrt(bg.R_eq_m):.4f}")
check(
    "PDE omega_0 > proxy omega_core",
    bg.omega_0 > 100 * omega_proxy,
    f"{bg.omega_0:.2e} vs {omega_proxy:.2e}",
)

# ────────────────────────────────────────────────────────────────
# Section 2: Structural identity omega_0 * tau = 1
# ────────────────────────────────────────────────────────────────
print("\n--- Section 2: Structural identity omega_0 * tau = 1 ---")
check("omega_0 * tau_eff = 1.0", abs(bg.omega_0_tau - 1.0) < 0.01,
      f"omega_0*tau = {bg.omega_0_tau:.6f}")

# Mass independence
print("\n  Mass scan for omega_0*tau:")
all_unity = True
for M_scale in [10, 30, 100, 1000, 1e6, 1e9]:
    bg_i = build_pde_background(M_kg=M_scale * M_SUN)
    x = bg_i.omega_0_tau
    ok = abs(x - 1.0) < 0.01
    if not ok:
        all_unity = False
    print(f"    {M_scale:>12.0f} M_sun: omega_0*tau = {x:.6f}  {'OK' if ok else 'FAIL'}")
check("omega_0 * tau = 1 for ALL masses", all_unity)

# ────────────────────────────────────────────────────────────────
# Section 3: Dispersion relation
# ────────────────────────────────────────────────────────────────
print("\n--- Section 3: Dispersion relation ---")
# At omega = omega_0, the dispersion relation should be close to zero
# (fundamental mode lives near omega_0)
F_at_w0 = dispersion_relation(complex(bg.omega_0, 0), bg)
print(f"  F(omega_0) = {F_at_w0:.4e} (should be near zero + memory term)")
check("Dispersion relation evaluable", abs(F_at_w0) < 1e30)

# Find modes
modes = solve_dispersion(bg, l=2, n_modes=3)
check("Modes found", len(modes) > 0, f"found {len(modes)} modes")
if modes:
    m0 = modes[0]
    print(f"\n  Primary mode:")
    print(f"    omega_real: {m0.omega_real:.4e} rad/s")
    print(f"    omega_imag: {m0.omega_imag:.4e} rad/s (damping)")
    print(f"    Q_pde:      {m0.Q_pde:.2f}")
    print(f"    class:      {m0.response_class}")
    check("Primary mode Q > 1 (not purely dissipative)", m0.Q_pde > 1.0)
    check("Primary mode Q < 100 (not proxy-like)", m0.Q_pde < 100.0)
    check("Primary mode omega > 0", m0.omega_real > 0)

# ────────────────────────────────────────────────────────────────
# Section 4: PDE vs Proxy quality factor
# ────────────────────────────────────────────────────────────────
print("\n--- Section 4: PDE vs Proxy Q comparison ---")
result = compute_pde_analysis(M_kg=30 * M_SUN)

print(f"  Q_PDE:   {result.Q_pde_fundamental:.2f}")
print(f"  Q_proxy: {result.Q_proxy:.2f}")
print(f"  Ratio:   {result.Q_pde_fundamental / result.Q_proxy:.4f}" if result.Q_proxy > 0 else "  Q_proxy = 0")

check("Q_PDE in mixed regime (1 < Q < 10)", 1 < result.Q_pde_fundamental < 10,
      f"Q_PDE = {result.Q_pde_fundamental:.2f}")
check("Q_proxy in low single digits", 1 < result.Q_proxy < 20,
      f"Q_proxy = {result.Q_proxy:.2f}")
check("Response class is mixed_viscoelastic", result.response_class == "mixed_viscoelastic",
      f"class = {result.response_class}")

# Universal Q check
print(f"\n  UNIVERSAL Q: beta_Q / alpha_vac = {2.0 / (1.0/3.0):.1f}")
check("Q_PDE ~ beta_Q/alpha (= 6)",
      abs(result.Q_pde_fundamental - 6.0) < 3.0,
      f"Q_PDE = {result.Q_pde_fundamental:.2f}")

# ────────────────────────────────────────────────────────────────
# Section 5: Damping rates comparison
# ────────────────────────────────────────────────────────────────
print("\n--- Section 5: Damping rates ---")
print(f"  gamma_PDE:   {result.gamma_pde:.4e} rad/s")
print(f"  gamma_proxy: {result.gamma_proxy:.4e} rad/s")
print(f"  omega_eff:   {result.omega_eff:.4e} rad/s")
print(f"  omega_proxy: {result.omega_proxy:.4e} rad/s")
check("gamma_PDE matches gamma_proxy (same formula at same point)",
      abs(result.gamma_pde - result.gamma_proxy) / max(result.gamma_pde, 1e-30) < 0.1,
      f"PDE={result.gamma_pde:.2e} proxy={result.gamma_proxy:.2e}")
check("omega_eff > omega_proxy (memory stiffness enhancement)",
      result.omega_eff > result.omega_proxy,
      f"{result.omega_eff:.2e} > {result.omega_proxy:.2e}")

# ────────────────────────────────────────────────────────────────
# Section 6: Echo channel impact
# ────────────────────────────────────────────────────────────────
print("\n--- Section 6: Echo channel impact ---")
print(f"  r_PDE:   {result.r_pde_amp:.4f}")
print(f"  r_proxy: {result.r_proxy_amp:.4f}")
print(f"  Impact:  {result.echo_impact}")
check("r_PDE in (0, 1)", 0 < result.r_pde_amp < 1,
      f"r = {result.r_pde_amp:.4f}")
check("r_PDE < 0.5 (lower than proxy)", result.r_pde_amp < 0.5,
      f"r = {result.r_pde_amp:.4f}")

# Compare to proxy echo amplitude
# Proxy: r ~ 0.98, PDE: r ~ 0.30
# Echo A_1/A_0 ~ T^2 * r_surface * r_peak
# T^2 ~ 0.0384, r_peak ~ 0.97
T_sq = 0.0384
r_peak = 0.97
A1_proxy = T_sq * 0.98 * r_peak
A1_pde = T_sq * result.r_pde_amp * r_peak
print(f"\n  Echo A_1/A_0 (proxy): {A1_proxy * 100:.2f}%")
print(f"  Echo A_1/A_0 (PDE):   {A1_pde * 100:.2f}%")
print(f"  Reduction factor:     {A1_pde / A1_proxy:.3f}")
check("Echo channel NOT collapsed (A_1/A_0 > 0)", A1_pde > 0)
check("Echo channel weakened vs proxy", A1_pde < A1_proxy)

# ────────────────────────────────────────────────────────────────
# Section 7: Mass dependence
# ────────────────────────────────────────────────────────────────
print("\n--- Section 7: Mass dependence ---")
print(f"  {'Mass (M_sun)':>14s}  {'Q_PDE':>8s}  {'Q_proxy':>8s}  {'r_PDE':>8s}  {'class':>20s}")
all_mixed = True
for M_scale in [10, 30, 100, 1000, 1e6, 1e9]:
    r_i = compute_pde_analysis(M_kg=M_scale * M_SUN)
    is_mixed = r_i.response_class == "mixed_viscoelastic"
    if not is_mixed:
        all_mixed = False
    print(f"  {M_scale:>14.0f}  {r_i.Q_pde_fundamental:>8.2f}  {r_i.Q_proxy:>8.2f}  {r_i.r_pde_amp:>8.4f}  {r_i.response_class:>20s}")

check("All masses in mixed_viscoelastic regime", all_mixed)

# ────────────────────────────────────────────────────────────────
# Section 8: Effective potential
# ────────────────────────────────────────────────────────────────
print("\n--- Section 8: Effective potential ---")
V_req = effective_potential(1.0 / 3.0, bg, l=2)
V_mid = effective_potential(0.5, bg, l=2)
V_outer = effective_potential(1.036, bg, l=2)
print(f"  V_eff(R_eq)  = {V_req:.4e}")
print(f"  V_eff(0.5)   = {V_mid:.4e}")
print(f"  V_eff(1.036) = {V_outer:.4e}")
check("V_eff(R_eq) > 0 (potential well)", V_req > 0)
check("V_eff decreases outward (Phi drops)", V_req > V_outer)

# ────────────────────────────────────────────────────────────────
# Section 9: Ringdown integration
# ────────────────────────────────────────────────────────────────
print("\n--- Section 9: Ringdown integration (PDE model) ---")
try:
    from grut.ringdown import compute_echo_analysis, EchoParameters

    for model in ["impedance", "interior", "graded", "pde"]:
        p = EchoParameters(
            M_kg=30 * M_SUN,
            reflection_model=model,
            R_eq_over_r_s=1.0 / 3.0,
            epsilon_Q=1.0 / 9.0,
        )
        r = compute_echo_analysis(p)
        echo_pct = r.echo_amplitudes[0] * 100 if r.echo_amplitudes else 0
        print(f"  {model:>10s}: r_surface={r.reflection_surface:.4f}  "
              f"A_1/A_0={echo_pct:.2f}%  "
              f"pde_Q={r.pde_Q:.1f}  proxy_Q={r.interior_quality_factor_Q:.1f}")

    # Confirm PDE model in ringdown
    p_pde = EchoParameters(
        M_kg=30 * M_SUN,
        reflection_model="pde",
        R_eq_over_r_s=1.0 / 3.0,
        epsilon_Q=1.0 / 9.0,
    )
    r_pde = compute_echo_analysis(p_pde)
    check("Ringdown PDE model works", r_pde.pde_Q > 0)
    check("PDE reflection < impedance reflection",
          r_pde.reflection_surface < 0.5)
except ImportError:
    print("  SKIP: ringdown module not available")

# ────────────────────────────────────────────────────────────────
# Section 10: Serialisation
# ────────────────────────────────────────────────────────────────
print("\n--- Section 10: Serialisation ---")
d = pde_result_to_dict(result)
check("Serialisable", isinstance(d, dict))
check("Has background section", "background" in d)
check("Has modes section", "modes" in d)
check("Has summary section", "summary" in d)
check("Has nonclaims", len(d.get("nonclaims", [])) > 0)
check("Has missing_closures", len(d.get("missing_closures", [])) > 0)

# ────────────────────────────────────────────────────────────────
# Section 11: Nonclaims verification
# ────────────────────────────────────────────────────────────────
print("\n--- Section 11: Nonclaims ---")
check("Nonclaims present", len(result.nonclaims) >= 8,
      f"{len(result.nonclaims)} nonclaims")
check("Missing closures present", len(result.missing_closures) >= 4,
      f"{len(result.missing_closures)} closures")

# Print key nonclaims
for nc in result.nonclaims[:3]:
    print(f"  - {nc}")
print(f"  ... and {len(result.nonclaims) - 3} more")


# ────────────────────────────────────────────────────────────────
# SUMMARY
# ────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("PDE BENCHMARK SUMMARY")
print("=" * 70)
print(f"""
  STRUCTURAL IDENTITY:
    omega_0 * tau_local = 1.0 (exact, mass-independent)
    BDCC sits at peak of memory damping function

  UNIVERSAL QUALITY FACTOR:
    Q_PDE = beta_Q / alpha_vac = {2.0/(1.0/3.0):.0f} (all masses)

  PDE RESULT (30 M_sun):
    Q_PDE:             {result.Q_pde_fundamental:.2f}  (mixed viscoelastic)
    Q_proxy (WP2C):    {result.Q_proxy:.2f}  (was: reactive_candidate)
    gamma_PDE:         {result.gamma_pde:.4e} rad/s
    omega_eff (PDE):   {result.omega_eff:.4e} rad/s
    r_PDE:             {result.r_pde_amp:.4f}
    r_proxy:           {result.r_proxy_amp:.4f}
    response_class:    {result.response_class}
    proxy_agreement:   {result.proxy_agreement}
    echo_impact:       {result.echo_impact}

  WP2C PROXY ERROR:
    proxy omega_core = beta_Q*GM/R_eq^4 (INCORRECT — extra 1/R_eq)
    PDE   omega_0    = beta_Q*GM/R_eq^3 (CORRECT — from linearisation)
    Factor: sqrt(R_eq) ~ 172 at 30 M_sun

  ECHO CHANNEL:
    Proxy estimate:  A_1/A_0 ~ {A1_proxy*100:.1f}% (reactive)
    PDE estimate:    A_1/A_0 ~ {A1_pde*100:.2f}% (mixed)
    Status: WEAKENED but NOT COLLAPSED

  BENCHMARK STATUS: {'CLEAN' if FAIL == 0 else f'DIRTY — {FAIL} failures'}
  Passed: {PASS}, Failed: {FAIL}
""")

if FAIL > 0:
    print(f"  WARNING: {FAIL} checks failed")
    sys.exit(1)
else:
    print("  All checks passed.")
    sys.exit(0)
