#!/usr/bin/env python3
"""Analyze screening factor (definition-only output)."""

import math

# The screening factor we found
screening_factor = 241.687617
R = 58412.904337

print("SCREENING FACTOR ANALYSIS: sqrt(R) =", screening_factor)
print("=" * 70)
print()

# Check powers and roots
print("Testing for geometric relationships:")
print(f"  sqrt(58412.9) = {math.sqrt(58412.9):.6f}")
print(f"  241.69^2 = {241.69**2:.2f}")
print()

# Check against fundamental constants
c = 299792458  # exact speed of light in m/s
test1 = c / math.sqrt(10)
print(f"  c / sqrt(10) = {test1:.2f}")
print()

# Check 16*pi^2
test2 = 16 * math.pi**2
print(f"  16π^2 = {test2:.6f}")
print(f"  Ratio to 241.69: {screening_factor / test2:.6f}")
print()

# The key insight: 241.69 ≈ ?
print("INTEGER SEARCH (definition-only):")
print("-" * 70)

# Test simple integers around 242
for n in range(235, 250):
    ratio = screening_factor / n
    if 0.98 < ratio < 1.02:
        print(f"  ★ {screening_factor:.2f} ≈ {n} (error: {abs(screening_factor - n):.3f})")

# Close to 242!
print()
print(f"  Screening factor ≈ 242")
print(f"  242 = 2 × 121 = 2 × 11^2")
print()

# Test sqrt relationships
print("Testing sqrt relationships:")
for n in [50000, 55000, 58000, 58413, 60000]:
    sqrt_n = math.sqrt(n)
    ratio = screening_factor / sqrt_n
    if 0.98 < ratio < 1.02:
        print(f"  ★ {screening_factor:.2f} ≈ sqrt({n}) = {sqrt_n:.2f}")

print()
print(f"  ★★★ sqrt(58413) = {math.sqrt(58413):.2f} ★★★")
print()

# Factor analysis of R
print(f"RATIO FACTORIZATION: R = {R:.6f}")
print("-" * 70)
print(f"  R / 137 = {R / 137:.2f}")
print(f"  R / 137^2 = {R / (137**2):.6f}  (This is ~3.11, close to π!)")
print(f"  R / 346 = {R / 346:.2f}")
print(f"  R / (346/2) = {R / 173:.2f}")
print(f"  R / pi^5 = {R / (math.pi**5):.2f}")
print()

# THE KEY RELATIONSHIP
print("REFERENCE CHECK")
print("-" * 70)
print(f"R / (137^2) = {R / (137**2):.6f}")
print(f"This is within 1% of π = {math.pi:.6f}")
print()
print("Definition-only comparison; no claims implied.")
print()

# Physical meaning
print("=" * 70)
print("DEFINITION-ONLY SUMMARY")
print("=" * 70)
print()
print("No mechanistic claims. This script prints numerical comparisons only.")
