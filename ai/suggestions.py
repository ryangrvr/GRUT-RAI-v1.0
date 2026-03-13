"""Enhanced experiment suggestion engine for GRUT-RAI."""

from __future__ import annotations

from typing import Any, Dict, List


def collect_suggestions(run: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate deterministic next-step suggestions based on a run result.

    Extends the original _collect_suggestions() with richer context.
    """
    resp = run.get("response", {}) if isinstance(run, dict) else {}
    kind = (run.get("kind") or "").lower()
    status = (run.get("status") or "").upper()

    suggestions: List[Dict[str, Any]] = []
    seen: set = set()

    def add(action: str, label: str, reason: str, confidence: str = "high"):
        if action in seen:
            return
        seen.add(action)
        suggestions.append({
            "action": action,
            "label": label,
            "reason": reason,
            "confidence": confidence,
        })

    # Cosmology run suggestions
    if kind.startswith("grut_run") or kind.startswith("cosmology"):
        add(
            "sweep_alpha_mem",
            "Sweep alpha_mem",
            "Run a parameter sweep varying alpha_mem from 0 to 1 to map memory sensitivity",
        )
        add(
            "compare_growth",
            "Check fsigma8 growth",
            "Enable growth to see if linear structure formation is consistent",
        )

    # fsigma8-related
    if "fsigma8" in kind or "fs8" in kind:
        add(
            "tau_search",
            "Search optimal tau",
            "Run Anamnesis tau search to find best-fit memory decay time",
        )
        add(
            "resonance_map",
            "Build resonance map",
            "Run leave-one-out diagnostics to identify high-leverage data points",
        )

    # Zeta-tau experiment
    if "zeta" in kind:
        if status == "PASS":
            add(
                "casimir_crosscheck",
                "Casimir cross-check",
                "PASS on zeta-tau suggests testing Casimir density consistency",
            )
        add(
            "pta_probe",
            "PTA dispersion probe",
            "Test whether GRUT dispersion survives PTA bounds",
        )

    # Casimir
    if "casimir" in kind:
        add(
            "pta_probe",
            "PTA dispersion probe",
            "Cross-check Casimir consistency with PTA dispersion limits",
        )

    # PTA
    if "pta" in kind:
        if status in ("PASS", "PASS_NOT_EXCLUDED"):
            add(
                "glass_transition",
                "Glass transition sweep",
                "PTA passed; test cosmological Deborah number",
            )

    # Anamnesis
    if "anamnesis" in kind or "reconstruct" in kind:
        add(
            "fsigma8_tau_search",
            "fsigma8 tau search",
            "Apply memory reconstruction to real fsigma8 data",
        )

    # Quantum boundary
    if "quantum" in kind:
        add(
            "mass_scan",
            "Quantum mass scan",
            "Sweep mass parameter to map decoherence boundary curve",
        )

    # General fallbacks
    if not suggestions:
        add(
            "explore_theory",
            "Explore GRUT theory",
            "Ask about tau0, memory kernels, or the observer layer",
            confidence="medium",
        )
        add(
            "run_baseline",
            "Run baseline cosmology",
            "Start with a standard matter-only run at z=2",
            confidence="medium",
        )

    return suggestions[:5]
