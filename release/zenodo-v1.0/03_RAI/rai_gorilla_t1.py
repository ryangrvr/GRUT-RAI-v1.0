#!/usr/bin/env python3
"""RAI-GORILLA T1 -- NEGATIVE-CONTROL REPAIR + CROSS-ONTOLOGY TEST. Gates the record.

Read-only. Banks nothing. W-0.

INSTRUMENT REPAIR (the defect this mission's own audit found in root1_kernel_origin.py and
rai_grut_resurrection.py, occurrence ~10 of the pass-label pattern): those instruments
transcribed agent verdicts into source literals and then "gated" the transcription -- the
gates verified typing fidelity, not the science, and one was labelled two-sided when its
outcome set excluded the alternative verdict by construction.

REPAIRED DESIGN, TWICE. First repair: every agent-produced verdict is READ FROM THE
WORKFLOW JOURNALS at gate time -- nothing agent-produced is a source literal. Second
repair, forced by the Section XIV hostile CATCHING the first repair re-committing the
defect: the first version still PINNED which verdict counts as passing (XIII passed only
on NOT-RESURRECTED), so a resurrecting outcome would have failed the battery -- a
story-pinned gate wearing journal clothes. NOW: verdicts flow journal -> record. Gates
assert (i) each agent returned a WELL-FORMED result and (ii) the committed record states
WHATEVER the journal says -- never which value it is. A different scientific outcome
changes the record, not the battery result. LIMIT, stated rather than papered over: for
free-text fields (the hostile's mechanism, the final statement) no mechanical gate can
certify QUALITY; those gates certify existence only, and the record says so.

Gate kinds: RECOMPUTE (re-derives physics; can fail on the physics) · JOURNAL (reads the
agent verdict from the journal; fails if the record disagrees with what the agents
actually returned) · GRAPH (walks the register) · QUOTE (citation fidelity only; no
verdict derives from a QUOTE gate).
"""
import json, hashlib, subprocess, sys, os, math, glob, re

ROOT = os.path.dirname(os.path.abspath(__file__))
WFBASE = ("/Users/mpg/.claude/projects/-Users-mpg-Library-Mobile-Documents-com-apple-"
          "CloudDocs-Ryans-Projects-GRUT-ResponsiveAI/7469561b-1dc7-4147-85e7-95af0652a664/"
          "subagents/workflows")
RUNS = {"negctl": "wf_596667f4-92b", "xont": "wf_963d7c83-112", "close": "wf_a096c8cb-141"}

def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()

def journal(run):
    out = []
    with open(os.path.join(WFBASE, RUNS[run], "journal.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                d = json.loads(line)
                if d.get("type") == "result": out.append(d.get("result"))
    return [r for r in out if isinstance(r, dict)]

FAILS, N = [], 0
def gate(cond, label, kind="GRAPH"):
    global N; N += 1
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {kind:9s} {label}")
    if not ok: FAILS.append(label)
    return ok

print("\n== A. GOVERNANCE / FREEZE ==")
reg = json.loads(read("provenance/claims.json"))
claims = reg["claims"] if isinstance(reg, dict) else reg
BY = {c["id"]: c for c in claims}
gate(len(claims) == 74, "register 74 nodes")
gate(hashlib.sha256(read("provenance/claims.json").encode()).hexdigest()
     .startswith("beaeb84e8a6f8468"), "register sha256 unchanged")
h = subprocess.run(["git","-C",ROOT,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
v = subprocess.run(["git","-C",ROOT,"rev-parse","origin/v4"],capture_output=True,text=True).stdout.strip()
gate(h == v, "HEAD == origin/v4 by ref identity")
porc = subprocess.run(["git","-C",ROOT,"status","--porcelain"],capture_output=True,text=True).stdout
gate(not any(l[:2] in (" M","M ","MM","D ") for l in porc.splitlines()),
     "no prior result retroactively modified")
gate("RESULTS_tt_worldline" not in porc and "tt_worldline_spectrum" not in porc,
     "contaminated instrument NOT patched -- provenance preserved")
for nid in ("u3_split_origin","u4_constitutive_origin"):
    gate(BY[nid].get("tier") == "to-derive", f"{nid} fence unmoved (to-derive)")

print("\n== B. SECTION III RECOMPUTED (two formulations, no shared code with the defect) ==")
def G_analytic(t, k1, k2, buggy=False, codilate=False):
    hi = k2*math.exp(t) if codilate else k2
    val = (1.0/(4*math.pi**2))*(math.log(hi/k1) + math.exp(-2*t)*(hi**2-k1**2)/2.0)
    return val/math.exp(2*t) if buggy else val
def G_numeric(t, k1, k2, buggy=False, codilate=False, n=4000):
    hi = k2*math.exp(t) if codilate else k2
    tot, dk = 0.0, (hi-k1)/n
    for i in range(n):
        k = k1 + (i+0.5)*dk
        amp2 = (1.0 + (k*math.exp(-t))**2)/(2.0*k**3)
        if buggy: amp2 /= math.exp(2*t)
        tot += (k*k/(2*math.pi**2))*amp2*dk
    return tot
gate(abs(G_numeric(2.0,20,60) - G_analytic(2.0,20,60))/G_analytic(2.0,20,60) < 1e-6,
     "formulations agree (numeric vs closed form)", "RECOMPUTE")
gate(G_analytic(4.0,20,60,buggy=True) < 1e-3 and G_analytic(4.0,20,60) > 0.04,
     "Finding 1 REVERSED: buggy collapses; correct asymptotes to ln3/(4pi^2)", "RECOMPUTE")
gate(G_analytic(4.0,20,60,codilate=True) > G_analytic(0.0,20,60,codilate=True),
     "correct comoving-IR/physical-UV GROWS (sign flip)", "RECOMPUTE")
gate(abs(G_analytic(0.0,20,60,buggy=True) - G_analytic(0.0,20,60)) < 1e-12,
     "at t=0 buggy==correct exactly: the sole prior gate sat at the blind point", "RECOMPUTE")

print("\n== C. NEGATIVE-CONTROL AUDIT (read from journal, not retyped) ==")
neg = journal("negctl")
audits = [r for r in neg if "blind_point_risk" in r]
gate(len(audits) == 6, f"six negatives audited (journal carries {len(audits)})", "JOURNAL")
reopen = [a for a in audits if a.get("verdict") == "MUST-BE-REOPENED"]
survive = [a for a in audits if a.get("verdict") in ("SURVIVES","SURVIVES-WEAKENED")]
gate(all(a.get("verdict") in ("SURVIVES","SURVIVES-WEAKENED","MUST-BE-REOPENED") for a in audits)
     and all(a.get("category") for a in audits),
     f"all six well-formed (journal tally: {len(reopen)} reopen / {len(survive)} survive "
     "-- reported, not a pass condition)", "JOURNAL")
std = [r for r in neg if "blind_point_doctrine" in r]
gate(len(std) == 1 and "N4" in (std[0].get("standard") or "")
     and "N5" in (std[0].get("standard") or ""),
     "the ten-element standard exists in the journal with N4/N5 demonstrated", "JOURNAL")

print("\n== D. CROSS-ONTOLOGY (read from journal) ==")
x = journal("xont")
dels = [r for r in x if "gap_survives" in r]
adj  = [r for r in x if "gap_in_two_non_aqft" in r]
gate(len(dels) == 2 and all(d.get("gap_survives") in
     ("GAP-SURVIVES","GAP-DISSOLVES","GAP-TRANSFORMS","UNDETERMINED") for d in dels),
     f"both deletion tests returned well-formed outcomes (journal: "
     f"{[d.get('gap_survives') for d in dels]} -- reported, not a pass condition)", "JOURNAL")
gate(len(adj) == 1 and adj[0].get("gap_in_two_non_aqft") in ("YES","NO","PARTIAL","UNDETERMINED"),
     f"adjudication well-formed (journal: {adj[0].get('gap_in_two_non_aqft') if adj else 'MISSING'} "
     "-- reported, not a pass condition)", "JOURNAL")
gate(all(len(d.get("smuggling_audit") or "") > 200 for d in dels),
     "both smuggling audits are substantive (graded field non-trivially filled)", "JOURNAL")

print("\n== E. CLOSEOUT XI-XV (journal-extracted; NO verdict value is a pass condition) ==")
c = journal("close")
xi   = [r for r in c if "closed_response_possible" in r]
xii  = [r for r in c if "anything_forces_finite_memory" in r]
xiii = [r for r in c if "reformulation_runs" in r]
xiv  = [r for r in c if "self_fooling_mechanism" in r]
xv   = [r for r in c if "smallest_statement" in r]
XI_S   = xi[0].get("closed_response_possible") if xi else None
XIII_S = xiii[0].get("status") if xiii else None
gate(XI_S in {"YES","NO","PARTIAL","UNDETERMINED"},
     f"XI returned a well-formed status (journal: {XI_S})", "JOURNAL")
gate(bool(xii) and bool(xii[0].get("anything_forces_finite_memory")),
     "XII returned its finite-memory adjudication (content not value-gated)", "JOURNAL")
gate(XIII_S in {"RESURRECTED","PARTIALLY-RESURRECTED","EFFECTIVE-THEORY","NOT-RESURRECTED",
                "REFUTED","QUESTION-MALFORMED"},
     f"XIII returned a well-formed status (journal: {XIII_S})", "JOURNAL")
gate(bool(xiv) and bool(xiv[0].get("self_fooling_mechanism")),
     "XIV hostile exists and filled its mechanism field (quality NOT mechanically certified)",
     "JOURNAL")
gate(bool(xv) and bool(xv[0].get("smallest_statement")),
     "XV exists and filled the final-statement field (quality NOT mechanically certified)",
     "JOURNAL")

print("\n== F. RECORD INTEGRITY (record must state what the JOURNAL says, whatever it says) ==")
rec = "RAI_GORILLA_T1.md"
if os.path.exists(os.path.join(ROOT, rec)):
    MD = re.sub(r"\s+"," ", read(rec).replace(">"," ").replace("*",""))
    gate("[[" not in MD, "no template token")
    DELS = [d.get("gap_survives") for d in dels]
    ADJ  = adj[0].get("gap_in_two_non_aqft") if adj else None
    needles = [(XI_S, "record states XI's journal status"),
               (XIII_S, "record states XIII's journal status"),
               (ADJ, "record states the cross-ontology adjudication"),
               ]
    for val, lbl in needles:
        gate(val is not None and val in MD, f"{lbl} ({val})")
    gate(all(d in MD for d in DELS), f"record states both deletion outcomes ({DELS})")
    gate(str(len(reopen)) in MD and "MUST-BE-REOPENED" in MD,
         f"record states the journal's reopen count ({len(reopen)})")
    gate("REVERSED" in MD, "record carries the Finding-1 reversal")
else:
    print("  [ -- ] record not yet written (first pass)")

print(f"\nBATTERY: {N-len(FAILS)}/{N}" + (f"  FAILURES: {FAILS}" if FAILS else ""))
print("W-0 -- reported, NOT banked. Register unmodified. Fences unmoved. A-F unselected.")
sys.exit(1 if FAILS else 0)
