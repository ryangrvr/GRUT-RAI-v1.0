from __future__ import annotations

from typing import Any, Dict, List

def _fmt(x: float, nd: int = 3) -> str:
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)

def build_narrative(prompt: str, nis: Dict[str, Any], out: Dict[str, Any]) -> Dict[str, Any]:
    """Translate engine + NIS into a narrative-first answer.

    This is intentionally deterministic and auditable (no black-box LLM).
    The frontend can render `text_markdown` and optionally the structured fields.
    """
    prompt = (prompt or "").strip()
    status = str(nis.get("status", "UNKNOWN")).upper()
    metabolic = str(nis.get("metabolic_state", "UNKNOWN")).upper()
    tension_color = str(nis.get("tension_color", "unknown")).lower()
    tension_score = float(nis.get("tension_score", 0.0))
    fuzz = float(nis.get("fuzz_fraction", 0.0))
    D = float(nis.get("D_eff", nis.get("I_heat", 0.0)))
    cap = float(nis.get("cap_engaged_frac", 0.0))
    deltaS = float(nis.get("deltaS", 0.0))
    I_value = float(nis.get("I_value", 1.0))
    profile = str(nis.get("observer_profile", "monk")).lower()

    # Pull a few optional values for clearer storytelling (still deterministic).
    cfl_value = float(nis.get("cfl_value", 0.0))
    handoff_margin = nis.get("handoff_margin")
    handoff_required = nis.get("handoff_required")
    g_min = nis.get("g_min")
    g_max = nis.get("g_max_obs")
    obs_mod = (out or {}).get("observer_modulation") or {}
    mod_enabled = bool(obs_mod.get("enabled", False))
    mod_multiplier = float(obs_mod.get("multiplier", 1.0))

    # A small, strict "confidence" heuristic:
    # PASS=0.95, WARN=0.75, FAIL=0.25; minus penalties for high tension & warnings.
    base_conf = {"PASS": 0.95, "WARN": 0.75, "FAIL": 0.25}.get(status, 0.5)
    warn_ct = len(nis.get("warnings") or [])
    conf = max(0.0, min(1.0, base_conf - 0.03 * warn_ct - 0.10 * max(0.0, tension_score - 0.6)))

    headline = {
        "PASS": "Sovereign run is stable.",
        "WARN": "Run is usable, but flagged.",
        "FAIL": "Run rejected by integrity gates.",
    }.get(status, "Run complete.")

    # Optional: respond to a classic prompt token without claiming anything extra.
    wants_42 = "42" in prompt
    if wants_42:
        intent_line = "You asked for the *why* behind “42”. In this system, “42” is not a mystical constant — it’s a **receipt**: a result plus the integrity trail that makes it admissible."
    elif prompt:
        intent_line = f"You asked: **{prompt}**"
    else:
        intent_line = "No prompt was provided; returning the default sovereign run."

    # --- Paragraph 1: Where you are (state summary)
    state_lines: List[str] = []
    if status == "PASS":
        state_lines.append("The run cleared every hard gate (CFL, bounds, phase handoff) and produced a reproducible certificate.")
    elif status == "WARN":
        state_lines.append("The run completed, but one or more guardrails flagged sensitivity. Treat results as exploratory until warnings are addressed.")
    else:
        state_lines.append("At least one integrity gate blocked the run. The system refused to fabricate a number outside the admissible regime.")

    if metabolic == "PIVOT":
        state_lines.append("You are in **PIVOT**: the sigmoid bridge is active, so small input changes can move outputs more than usual.")
    elif metabolic == "STRESS":
        state_lines.append("You are in **STRESS**: the observer/tension channels are elevated relative to baseline.")
    elif metabolic == "CALM":
        state_lines.append("You are in **CALM**: far from the handoff and numerically quiet.")

    # --- Paragraph 2: What moved (observer modulation summary)
    if mod_enabled:
        moved = (
            f"Observer modulation is **enabled** and currently routes through **dissipation** only: "
            f"ΔS={_fmt(deltaS,4)} produced a multiplier of {_fmt(mod_multiplier,3)}, yielding D_eff={_fmt(D,6)}."
        )
    else:
        moved = (
            "Observer modulation is **disabled** (or not active), so the observer layer is reported for transparency but does not alter cosmology outputs."
        )

    # --- Paragraph 3: Why “42” (promise of the portal)
    if wants_42:
        forty_two = (
            "Why this answers “42”: because every headline is backed by the expandable panel — equations, raw arrays, and the NIS certificate. "
            "If the certificate fails, the portal refuses the narrative."
        )
    else:
        forty_two = ""

    # Top metrics table (tight + scannable)
    rows = [
        ("NIS", status),
        ("Metabolic state", metabolic),
        ("Tension", f"{_fmt(tension_score,3)} ({tension_color})"),
        ("Fuzz fraction εt/τ0", _fmt(fuzz, 6)),
        ("D_eff", _fmt(D, 6)),
        ("Cap engaged", _fmt(cap, 3)),
        ("Observer profile", profile),
        ("ΔS", _fmt(deltaS, 4)),
        ("I", _fmt(I_value, 3)),
        ("CFL", _fmt(cfl_value, 6)),
    ]
    if handoff_required is not None and handoff_margin is not None:
        rows.append(("Handoff margin", f"{_fmt(float(handoff_margin),6)} (req { _fmt(float(handoff_required),6) })"))
    if g_min is not None and g_max is not None:
        rows.append(("Gain range", f"[{_fmt(float(g_min),6)}, {_fmt(float(g_max),6)}]"))

    table = "| Metric | Value |\n|---|---|\n" + "\n".join([f"| {k} | `{v}` |" for k, v in rows])

    text_parts: List[str] = [
        f"**{headline}**\n\n{intent_line}\n",
        "\n".join(state_lines) + "\n",
        moved + "\n",
    ]
    if forty_two:
        text_parts.append(forty_two + "\n")
    text_parts.append("\n**Top metrics (scannable)**\n" + table + "\n")

    text = "\n".join([p.strip() for p in text_parts if p.strip()]) + "\n"

    # Add short “what it means” paragraph, keeping it physics-neutral.
    # Keep a final single-sentence meaning line for users who skim.
    if status == "PASS":
        meaning = "Interpretation: internally consistent under current settings; observer effects (if active) remain in dissipation, not gain/memory."
    elif status == "WARN":
        meaning = "Interpretation: usable with caution; review warnings and consider finer z-grid or calmer observer settings."
    else:
        meaning = "Interpretation: rejected by integrity; adjust εt/velocities until CFL and bounds pass."
    text += f"\n_{meaning}_\n"

    # Recommendations (frontend-friendly)
    rec: List[str] = []
    if status != "PASS":
        rec.append("Reduce v_obs / v_grid, or increase εt until CFL passes.")
    if tension_score >= 0.6:
        rec.append("Lower UI entropy or switch to Astronomer/Monk to reduce metric tension.")
    if warn_ct:
        rec.append("Open the NIS certificate and address listed warnings before interpreting outputs.")
    if not rec:
        rec.append("Open the expandable panel for raw outputs and the reproducible NIS certificate.")

    return {
        "text_markdown": text,
        "headline": headline,
        "confidence": conf,
        "key": {
            "nis": status,
            "metabolic_state": metabolic,
            "tension": {"score": tension_score, "color": tension_color},
            "fuzz_fraction": fuzz,
            "D_eff": D,
            "cap_engaged_frac": cap,
            "observer_profile": profile,
            "deltaS": deltaS,
            "I_value": I_value,
        },
        "recommendations": rec,
    }
