"""Anamnesis / Numerical Reconstruction Lens.

This package provides a *general* inverse-problem pipeline:

Forward (simulator.py):   x (source) -> y (shadow) via a causal smear kernel
Inverse (reconstructor.py): y -> x_hat via Locally Competitive Algorithm (LCA)
Judge (evaluator.py):    score/compare with Earth Mover's Distance (EMD) + metrics

The initial implementation is intentionally 1D and dependency-light so it can
ship as a hardened demo and later be upgraded to higher-dimensional cosmology
reconstructions.
"""
