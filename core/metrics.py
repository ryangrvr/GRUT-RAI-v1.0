"""Simple scoring utilities for baseline comparisons (MVP).

Provides L2 and chi2 metrics and a delta helper.
"""
from typing import Optional
import numpy as np


def l2_score(y_true, y_model):
    y_true = np.asarray(y_true, dtype=float)
    y_model = np.asarray(y_model, dtype=float)
    if y_true.shape != y_model.shape:
        raise ValueError("Shapes must match for L2 score")
    return float(np.linalg.norm(y_true - y_model))


def chi2_score(y_true, y_model, sigma):
    y_true = np.asarray(y_true, dtype=float)
    y_model = np.asarray(y_model, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    if y_true.shape != y_model.shape or sigma.shape != y_true.shape:
        raise ValueError("Shapes must match for chi2")
    return float(np.sum(((y_true - y_model) / (sigma + 1e-12)) ** 2))


def delta_score(score_grut: float, score_baseline: float) -> float:
    """Return difference (grut - baseline). Negative => grut better (lower)."""
    return float(score_grut - score_baseline)
