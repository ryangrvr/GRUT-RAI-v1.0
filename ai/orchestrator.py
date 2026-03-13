"""Main AI orchestration loop for GRUT-RAI.

Handles the tool-use conversation loop: user message -> Claude -> tool calls
-> engine results -> Claude narration -> response.

Falls back to deterministic narrative when no API key is available.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ai.client import get_ai_client
from ai.system_prompt import build_system_prompt
from ai.tools import get_tool_definitions
from ai.tool_executor import execute_tool

logger = logging.getLogger(__name__)

# Keywords for fallback intent detection (enhanced from original)
INTENT_KEYWORDS = [
    "run", "h(z)", "hz", "hubble", "fsigma8", "growth", "simulate",
    "sweep", "compute", "calculate", "show me", "plot", "chart",
]
EXPERIMENT_KEYWORDS = [
    "zeta", "casimir", "pta", "glass transition", "experiment",
]
THEORY_KEYWORDS = [
    "what is", "explain", "how does", "tell me about", "define",
    "tau0", "alpha_mem", "memory kernel", "observer", "nis",
    "dissipation", "screening", "canon",
]


@dataclass
class AIResponse:
    """Response from the AI orchestrator."""
    text_markdown: str
    charts: List[Dict[str, Any]] = field(default_factory=list)
    run_ids: List[str] = field(default_factory=list)
    suggestions: List[Dict[str, Any]] = field(default_factory=list)
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    certificate_summary: Optional[Dict[str, Any]] = None
    nis_status: Optional[str] = None
    fallback_used: bool = False


def respond(
    user_message: str,
    conversation_history: Optional[List[Dict[str, Any]]] = None,
    *,
    grut_engine: Any = None,
    db_store: Any = None,
    engine_version: str = "",
    params_hash: str = "",
    response_mode: str = "standard",
) -> AIResponse:
    """Process a user message and return an AI response.

    Parameters
    ----------
    response_mode : str
        "standard" (default) -- narrated explanations.
        "forensic" -- structured JSON only, no narrative.

    If Claude API is available, uses tool-use for intelligent responses.
    Otherwise falls back to deterministic keyword matching.
    """
    client = get_ai_client()

    if not client.available:
        return _fallback_respond(user_message, grut_engine=grut_engine, db_store=db_store)

    # Build messages list
    messages: List[Dict[str, Any]] = []
    if conversation_history:
        for msg in conversation_history[-20:]:  # last 20 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                messages.append({"role": role, "content": content})

    messages.append({"role": "user", "content": user_message})

    system = build_system_prompt(engine_version, params_hash, response_mode=response_mode)
    tools = get_tool_definitions()

    # Tool-use loop (max 5 rounds to prevent infinite loops)
    all_tool_results: List[Dict[str, Any]] = []
    charts: List[Dict[str, Any]] = []
    run_ids: List[str] = []
    cert_summary = None
    nis_status = None

    for turn in range(5):
        response = client.chat(messages=messages, system=system, tools=tools)

        if response is None:
            return _fallback_respond(user_message, grut_engine=grut_engine, db_store=db_store)

        # Check if Claude wants to use tools
        tool_use_blocks = [
            block for block in response.content
            if block.type == "tool_use"
        ]
        text_blocks = [
            block.text for block in response.content
            if block.type == "text"
        ]

        if not tool_use_blocks:
            # No more tool calls, Claude is done
            final_text = "\n".join(text_blocks)
            return AIResponse(
                text_markdown=final_text,
                charts=charts,
                run_ids=run_ids,
                tool_results=all_tool_results,
                certificate_summary=cert_summary,
                nis_status=nis_status,
            )

        # Execute tool calls and feed results back
        # First, add Claude's response (with tool_use blocks) to messages.
        # Convert Pydantic model objects to plain dicts to avoid serialization
        # issues with anthropic SDK + Pydantic v2 (by_alias bug).
        serialized_content = []
        for block in response.content:
            if block.type == "text":
                serialized_content.append({"type": "text", "text": block.text})
            elif block.type == "tool_use":
                serialized_content.append({
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                })
        messages.append({"role": "assistant", "content": serialized_content})

        tool_results_for_message = []
        for tool_block in tool_use_blocks:
            result = execute_tool(
                tool_block.name,
                tool_block.input,
                grut_engine=grut_engine,
                db_store=db_store,
            )

            all_tool_results.append({
                "tool": tool_block.name,
                "input": tool_block.input,
                "result": result,
            })

            # Extract charts and certificate info
            if "charts" in result:
                for chart_type, chart_data in result["charts"].items():
                    if chart_data:
                        charts.append({"type": chart_type, "data": chart_data})

            if "certificate" in result:
                cert_summary = result["certificate"]
                # NIS status from viability or cert
                viability = result.get("viability", {})
                nis_status = viability.get("status", "PASS")

            tool_results_for_message.append({
                "type": "tool_result",
                "tool_use_id": tool_block.id,
                "content": json.dumps(result, default=str),
            })

        messages.append({"role": "user", "content": tool_results_for_message})

    # If we exhausted the loop
    final_text = "\n".join(text_blocks) if text_blocks else "I ran the requested simulations. See the results above."
    return AIResponse(
        text_markdown=final_text,
        charts=charts,
        run_ids=run_ids,
        tool_results=all_tool_results,
        certificate_summary=cert_summary,
        nis_status=nis_status,
    )


def _fallback_respond(
    user_message: str,
    *,
    grut_engine: Any = None,
    db_store: Any = None,
) -> AIResponse:
    """Deterministic fallback when Claude API is unavailable.

    Enhanced from the original _determine_intent() with richer responses.
    """
    msg_lower = (user_message or "").strip().lower()

    # Check for theory questions
    if any(kw in msg_lower for kw in THEORY_KEYWORDS):
        return _fallback_theory(msg_lower)

    # Check for experiment requests
    if any(kw in msg_lower for kw in EXPERIMENT_KEYWORDS):
        return AIResponse(
            text_markdown=(
                "**Experiment mode** (AI offline)\n\n"
                "I can run experiments but need the AI layer for natural language interpretation. "
                "Use the Experiments tab to launch experiments directly, or set "
                "`ANTHROPIC_API_KEY` to enable conversational experiment control."
            ),
            fallback_used=True,
        )

    # Check for run requests
    if any(kw in msg_lower for kw in INTENT_KEYWORDS):
        if grut_engine is not None:
            result = execute_tool(
                "run_cosmology",
                {"enable_growth": True},
                grut_engine=grut_engine,
                db_store=db_store,
            )

            charts = []
            if "charts" in result:
                for ct, cd in result["charts"].items():
                    if cd:
                        charts.append({"type": ct, "data": cd})

            cert = result.get("certificate", {})
            text = (
                "**Phase-2 run completed** (deterministic mode)\n\n"
                f"Integrator: {cert.get('integrator', 'RK4')} | "
                f"Steps: {cert.get('steps_computed', '?')} | "
                f"Observables: {', '.join(cert.get('observables_emitted', []))}\n\n"
                f"Canon hash: `{cert.get('canon_hash', '?')[:16]}...`\n"
                f"Repro hash: `{cert.get('repro_hash', '?')[:16]}...`\n\n"
                "_Set ANTHROPIC_API_KEY for intelligent narration of results._"
            )

            return AIResponse(
                text_markdown=text,
                charts=charts,
                certificate_summary=cert,
                fallback_used=True,
            )

    # Default chat response
    return AIResponse(
        text_markdown=(
            f'Received: "{user_message}"\n\n'
            "I'm running in deterministic mode (no AI key configured). "
            "I can still run the engine -- try saying **\"run H(z)\"** or use the tabs above.\n\n"
            "Set `ANTHROPIC_API_KEY` to enable full Responsive AI capabilities."
        ),
        fallback_used=True,
    )


def _fallback_theory(msg_lower: str) -> AIResponse:
    """Provide basic theory explanations without the LLM."""
    explanations = {
        "tau0": (
            "**tau0 (41.9 Myr)** is the canonical memory relaxation timescale in GRUT. "
            "The universe 'remembers' its expansion history over this window via an "
            "exponential retarded kernel: K(s) = (1/tau_eff) exp(-s/tau_eff) for s > 0. "
            "The ODE equivalent: tau_eff * dM/dt + M = H_base^2."
        ),
        "alpha_mem": (
            "**alpha_mem** controls the weight of memory-smoothed correction to the Hubble parameter. "
            "H^2 = (1 - alpha_mem) * H_base^2 + alpha_mem * M_X. "
            "Setting alpha_mem = 0 recovers standard cosmology; alpha_mem = 1 is full memory correction. "
            "Canon default: 0.1, tunable in [0, 1]."
        ),
        "memory kernel": (
            "The **GRUT memory kernel** is an exponential retarded kernel: "
            "K(s) = (1/tau_eff) exp(-s/tau_eff) * Theta(s), with integral normalized to 1. "
            "It is strictly causal (retarded: only past states contribute). "
            "The equivalent ODE is: tau_eff * dM_X/dt + M_X = X(t), where X = H_base^2."
        ),
        "observer": (
            "The **observer layer** has three profiles:\n"
            "- **Monk**: Zero engagement (baseline)\n"
            "- **Astronomer**: Sensor-dominant (w_ui=0.2, w_sensor=0.8)\n"
            "- **Participant**: UI-dominant (w_ui=0.9, w_sensor=0.1)\n\n"
            "deltaS = w_ui * UI_entropy + w_sensor * Sensor_flux. "
            "When observer modulation is enabled, this scales dissipation D(z)."
        ),
        "nis": (
            "**NIS (Numerical Integrity Standard)** provides reproducibility certificates. "
            "Each run gets a SHA-256 determinism stamp over inputs + code_version + seed. "
            "Hard gates: CFL (causal integrity), gain bounds [1, 4/3], handoff accounting. "
            "Status: PASS (all gates cleared), WARN (flagged), FAIL (rejected)."
        ),
        "dissipation": (
            "**Dissipation D(z)** is positive-definite damping applied each step: "
            "H := H * exp(-gamma_H * dt). With observer modulation enabled: "
            "D *= (1 + lambda * deltaS), clamped to [0.5, 3.0]. "
            "D is bounded at 0.999 (cannot fully erase)."
        ),
        "screening": (
            "**Screening S = 108pi** is the vacuum screening factor. "
            "It relates the cosmological timescale tau_Lambda = H0^(-1) to the "
            "memory timescale tau0 = tau_Lambda / S. "
            "Derived from alpha_vac = 1/3: S = 12pi / alpha_vac^2 = 108pi."
        ),
    }

    for key, explanation in explanations.items():
        if key in msg_lower:
            return AIResponse(
                text_markdown=explanation + "\n\n_Running in deterministic mode._",
                fallback_used=True,
            )

    return AIResponse(
        text_markdown=(
            "I can explain GRUT theory topics. Try asking about:\n"
            "- **tau0** (memory timescale)\n"
            "- **alpha_mem** (memory coupling)\n"
            "- **memory kernel** (causal kernel)\n"
            "- **observer** (observer profiles)\n"
            "- **NIS** (integrity certificates)\n"
            "- **dissipation** (damping operator)\n"
            "- **screening** (vacuum screening)\n\n"
            "_Set ANTHROPIC_API_KEY for deeper, contextual explanations._"
        ),
        fallback_used=True,
    )
