#!/usr/bin/env python3
"""Casimir Density Sweep (definition-only output).

Computes baseline-defined τΛ = H0^-1 and compares densities using τ0 = 41.9 Myr.
No mechanistic claims are made.
"""

import math

# ============================================================================
# STEP 1: CONSTANTS
# ============================================================================

# Fundamental constants
G = 6.674e-11  # Gravitational constant [m^3 kg^-1 s^-2]
c = 2.998e8    # Speed of light [m/s]

# Time conversion
MYR_TO_SEC = 3.154e13  # 1 Myr in seconds

# Target metric relaxation time
TAU_TARGET_MYR = 41.9
TAU_TARGET_SEC = TAU_TARGET_MYR * MYR_TO_SEC

# Baseline-defined cosmological parameters
H0_KM_S_MPC = 67.36       # Hubble constant [km/s/Mpc]
OMEGA_LAMBDA = 0.6847     # Dark energy density parameter
OMEGA_M = 0.315           # Matter density parameter

# Unit conversions for Hubble constant
MPC_TO_M = 3.086e22       # 1 Megaparsec in meters
KM_TO_M = 1000.0

# Fine structure constant
ALPHA = 1.0 / 137.035999  # Fine structure constant
ALPHA_INV = 137.035999    # Inverse fine structure constant

print("=" * 80)
print("CASIMIR DENSITY HYPOTHESIS — Physical Grounding of tau_0 = 41.9 Myr")
print("=" * 80)
print()

# ============================================================================
# STEP A: Calculate Cosmological Vacuum Density (rho_Lambda)
# ============================================================================

print("STEP A: COSMOLOGICAL VACUUM DENSITY (Dark Energy)")
print("-" * 80)

# Convert H0 to SI units [s^-1]
H0_SI = (H0_KM_S_MPC * KM_TO_M) / MPC_TO_M

# Critical density: rho_crit = 3 H0^2 / (8 pi G)
rho_crit = (3.0 * H0_SI**2) / (8.0 * math.pi * G)

# Dark energy density: rho_Lambda = Omega_Lambda * rho_crit
rho_Lambda = OMEGA_LAMBDA * rho_crit

print(f"H0 = {H0_KM_S_MPC} km/s/Mpc = {H0_SI:.6e} s^-1")
print(f"Critical density: rho_crit = {rho_crit:.6e} kg/m^3")
print(f"Omega_Lambda = {OMEGA_LAMBDA}")
print(f"Dark energy density: rho_Lambda = {rho_Lambda:.6e} kg/m^3")
print()

# ============================================================================
# STEP B: Calculate Required Density for tau_0 = 41.9 Myr
# ============================================================================

print("STEP B: REQUIRED DENSITY FOR tau_0 = 41.9 Myr")
print("-" * 80)

# Formula: tau = 1 / sqrt(8 * pi * G * rho)
# Solving for rho: rho_req = 1 / (8 * pi * G * tau^2)

rho_req = 1.0 / (8.0 * math.pi * G * TAU_TARGET_SEC**2)

print(f"Target relaxation time: tau_0 = {TAU_TARGET_MYR} Myr = {TAU_TARGET_SEC:.6e} s")
print(f"Formula: tau = 1 / sqrt(8 π G rho)")
print(f"Inverted: rho_req = 1 / (8 π G tau^2)")
print(f"Required density: rho_req = {rho_req:.6e} kg/m^3")
print()

# ============================================================================
# STEP 3: THE COMPARISON — The Discovery Step
# ============================================================================

print("STEP 3: DENSITY RATIO ANALYSIS")
print("-" * 80)

# Primary ratio
R = rho_req / rho_Lambda

print(f"Ratio: R = rho_req / rho_Lambda = {R:.6f}")
print(f"       R = {R:.10e}")
print()

# Screening factor
screening_factor = math.sqrt(R)

print(f"Screening Factor: sqrt(R) = {screening_factor:.6f}")
print()

# ============================================================================
# SOVEREIGN INTEGER / GEOMETRIC CONSTANT SEARCH
# ============================================================================

print("SOVEREIGN INTEGER SEARCH:")
print("-" * 80)

# Test 1: Fine structure constant relationships
alpha_inv_squared = ALPHA_INV**2
ratio_to_alpha_inv_sq = R / alpha_inv_squared

print(f"1. Fine Structure Constant Inverse: α^-1 = {ALPHA_INV:.6f}")
print(f"   α^-1 squared: {alpha_inv_squared:.2f}")
print(f"   R / (α^-1)^2 = {ratio_to_alpha_inv_sq:.6f}")
if 0.9 < ratio_to_alpha_inv_sq < 1.1:
    print(f"   ★★★ MATCH: R ≈ (137)^2 ★★★")
print()

# Test 2: Powers of 10
log10_R = math.log10(R)
nearest_power_10 = round(log10_R)
power_10_ratio = R / (10**nearest_power_10)

print(f"2. Powers of 10:")
print(f"   log10(R) = {log10_R:.6f}")
print(f"   Nearest power: 10^{nearest_power_10} = {10**nearest_power_10:.6e}")
print(f"   R / 10^{nearest_power_10} = {power_10_ratio:.6f}")
if 0.9 < power_10_ratio < 1.1:
    print(f"   ★★★ MATCH: R ≈ 10^{nearest_power_10} ★★★")
print()

# Test 3: Speed of light normalized (various powers)
c_normalized_1 = R / c
c_normalized_2 = R / (c**2)
c_normalized_3 = R / math.sqrt(c)

print(f"3. Speed of Light Normalization:")
print(f"   R / c = {c_normalized_1:.6e}")
print(f"   R / c^2 = {c_normalized_2:.6e}")
print(f"   R / sqrt(c) = {c_normalized_3:.6e}")
print()

# Test 4: Check against 346 (from zeta test) and related numbers
zeta_candidate = 346
zeta_squared = zeta_candidate**2
ratio_to_346_sq = R / zeta_squared

print(f"4. Zeta Test Number (346):")
print(f"   346^2 = {zeta_squared}")
print(f"   R / 346^2 = {ratio_to_346_sq:.6f}")
if 0.9 < ratio_to_346_sq < 1.1:
    print(f"   ★★★ MATCH: R ≈ 346^2 ★★★")
print()

# Test 5: Small integer multiples
small_integers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 32, 64, 100, 128, 256]
print(f"5. Small Integer Factors:")
for n in small_integers:
    if 0.95 < R / n < 1.05:
        print(f"   ★ R ≈ {n} (ratio = {R/n:.4f})")
print()

# Test 6: Check if it's close to pi, e, or their combinations
pi_multiples = [
    ("π", math.pi),
    ("π^2", math.pi**2),
    ("π^3", math.pi**3),
    ("2π", 2 * math.pi),
    ("4π", 4 * math.pi),
    ("e", math.e),
    ("e^2", math.e**2),
    ("π*e", math.pi * math.e),
]

print(f"6. Mathematical Constants:")
for name, value in pi_multiples:
    ratio = R / value
    if 0.9 < ratio < 1.1:
        print(f"   ★ R / {name} = {ratio:.6f}")
print()

# ============================================================================
# PHYSICAL INTERPRETATION
# ============================================================================

print("=" * 80)
print("PHYSICAL INTERPRETATION")
print("=" * 80)
print()

print(f"If the vacuum is reacting at tau_0 = {TAU_TARGET_MYR} Myr, it 'thinks' the")
print(f"effective density is:")
print()
print(f"  rho_effective = {rho_req:.6e} kg/m^3")
print()
print(f"This is {R:.2f}× higher than the cosmological dark energy density.")
print()
print(f"Screening Factor: {screening_factor:.2f}")
print()
print("Definition-only output (no mechanistic claims).")
print()

# Additional ratios
print("DENSITY HIERARCHY:")
print("-" * 80)
print(f"rho_req / rho_Lambda = {R:.6f}")
print(f"rho_req / rho_crit   = {rho_req / rho_crit:.6f}")
print(f"rho_Lambda / rho_crit = {OMEGA_LAMBDA:.6f}")
print()

# Time scale comparisons (baseline-defined)
tau_lambda = 1.0 / H0_SI
tau_lambda_myr = tau_lambda / MYR_TO_SEC

print("TIME SCALE COMPARISON:")
print("-" * 80)
print(f"tau_0 (observed)         = {TAU_TARGET_MYR} Myr")
print(f"tau_Lambda (baseline-defined H0^-1) = {tau_lambda_myr:.2f} Myr")
print(f"Ratio: tau_Lambda / tau_0 = {tau_lambda_myr / TAU_TARGET_MYR:.6f}")
print(f"Reference: screening_factor = {screening_factor:.6f}")
print()

print("=" * 80)
print("CASIMIR DENSITY HYPOTHESIS: COMPLETE")
print("=" * 80)
