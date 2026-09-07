#!/usr/bin/env python3
"""RAI-DIALECTIC -- BUILDER/WRECKER CHAMBER. Gates the committed record.

Read-only. Banks nothing. W-0. Register untouched; u3/u4 fences unmoved.

DESIGN (the twice-caught lesson applied from the start): every chamber verdict is READ FROM
THE WORKFLOW JOURNAL at gate time and NO verdict value is a pass condition. Gates assert
(i) well-formedness of each agent result, (ii) that the record states WHATEVER the journal
says, and (iii) live recomputation of the two mechanically checkable corpus claims. A
different chamber outcome would change the record, not the battery. Free-text quality is not
mechanically certifiable and is not certified.
"""
import json, hashlib, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
JPATH = ("/Users/mpg/.claude/projects/-Users-mpg-Library-Mobile-Documents-com-apple-"
         "CloudDocs-Ryans-Projects-GRUT-ResponsiveAI/7469561b-1dc7-4147-85e7-95af0652a664/"
         "subagents/workflows/wf_3215b415-fe5/journal.jsonl")

def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()

FAILS, N = [], 0
def gate(cond, label, kind="JOURNAL"):
    global N; N += 1
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {kind:9s} {label}")
    if not ok: FAILS.append(label)
    return ok

print("\n== A. GOVERNANCE ==")
reg = json.loads(read("provenance/claims.json"))
claims = reg["claims"] if isinstance(reg, dict) else reg
BY = {c["id"]: c for c in claims}
gate(len(claims) == 74, "register 74 nodes", "GRAPH")
gate(hashlib.sha256(read("provenance/claims.json").encode()).hexdigest()
     .startswith("beaeb84e8a6f8468"), "register sha256 unchanged", "GRAPH")
h = subprocess.run(["git","-C",ROOT,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
v = subprocess.run(["git","-C",ROOT,"rev-parse","origin/v4"],capture_output=True,text=True).stdout.strip()
gate(h == v, "HEAD == origin/v4 by ref identity", "GRAPH")
porc = subprocess.run(["git","-C",ROOT,"status","--porcelain"],capture_output=True,text=True).stdout
gate(not any(l[:2] in (" M","M ","MM","D ") for l in porc.splitlines()),
     "no prior result modified", "GRAPH")
for nid in ("u3_split_origin","u4_constitutive_origin"):
    gate(BY[nid].get("tier") == "to-derive", f"{nid} fence unmoved", "GRAPH")

print("\n== B. CHAMBER JOURNAL (well-formedness only; no verdict is a pass condition) ==")
res = []
with open(JPATH, encoding="utf-8") as f:
    for line in f:
        if line.strip():
            d = json.loads(line)
            if d.get("type") == "result" and isinstance(d.get("result"), dict):
                res.append(d["result"])
turns = [r for r in res if "convergence_signal" in r]
outs  = [r for r in res if "strongest_hidden_assumption" in r]
sas   = [r for r in res if "strongest_wrongness" in r]
fins  = [r for r in res if "s1_survivor" in r]
gate(len(turns) >= 6, f"blind round-1 pair + dialectic rounds exist ({len(turns)} turns)")
SIGS = [t.get("convergence_signal") for t in turns]
gate(all(s in ("CONTINUE","AGREEMENT","CONDITIONAL-AGREEMENT","IRREDUCIBLE-DISAGREEMENT","COLLAPSE")
         for s in SIGS), f"all signals well-formed (sequence: {SIGS} -- reported, not a pass condition)")
changes = sum(1 for t in turns if (t.get("position_changes") or "").strip().upper() not in ("","NONE")
              and "NONE (" not in (t.get("position_changes") or ""))
gate(changes >= 2, f"belief revision actually occurred ({changes} turns carry V-format changes)")
gate(len(outs) == 1 and outs[0].get("verdict") in ("GENUINE-CONVERGENCE","MUTUAL-REINFORCEMENT","MIXED"),
     f"outsider ran, blinded, well-formed (verdict: {outs[0].get('verdict') if outs else 'MISSING'})")
gate(len(sas) == 2 and all(s.get("strongest_wrongness") for s in sas),
     "both self-attacks exist and filled the wrongness field")
F = fins[0] if fins else {}
CONV = F.get("convergence_class"); GRUT = F.get("s8_grut_status")
gate(CONV in ("A-AGREEMENT","B-CONDITIONAL-AGREEMENT","C-IRREDUCIBLE-DISAGREEMENT","D-COLLAPSE"),
     f"final synthesis convergence class well-formed (journal: {CONV})")
gate(GRUT in ("FOUNDATIONAL","EMERGENT","EFFECTIVE","PARTIAL","REFUTED","MALFORMED",
              "IRRELEVANT-TO-FINAL-STRUCTURE","UNDETERMINED"),
     f"GRUT status well-formed (journal: {GRUT})")
gate(all(F.get(k) for k in ("s1_survivor","x1_smallest_unremovable","x2_what_would_falsify_it",
                            "x3_if_grut_disappeared","s10_gorilla","s12_next_test")),
     "XVII/XVIII required fields all present (content not value-gated)")

print("\n== C. THE TWO MECHANICALLY CHECKABLE CORPUS CLAIMS (recomputed live) ==")
gg = subprocess.run(["git","-C",ROOT,"grep","-l","ordinary input"],capture_output=True,text=True)
gate(gg.stdout.strip() == "" and gg.returncode == 1,
     "'ordinary input' occurs in ZERO committed files -- the endgame predicate was unfrozen",
     "RECOMPUTE")
pm = read("POSTULATE_MAP.md")
gate("The Born measure" in pm and "laundering" in pm,
     "Bin 1 carries the Born measure + the laundering doctrine (the preload and the unsorted door)",
     "QUOTE")

print("\n== D. RECORD/JOURNAL CONSISTENCY (dynamic needles) ==")
rec = "RAI_DIALECTIC_CHAMBER.md"
if os.path.exists(os.path.join(ROOT, rec)):
    MD = re.sub(r"\s+"," ", read(rec).replace(">"," ").replace("*",""))
    gate("[[" not in MD, "no template token", "GRAPH")
    for val, lbl in ((CONV, "record states the journal's convergence class"),
                     (GRUT, "record states the journal's GRUT status"),
                     (outs[0].get("verdict") if outs else None, "record states the outsider verdict")):
        # match on the value with hyphens or spaces (record renders 'B — CONDITIONAL AGREEMENT')
        ok = val is not None and (val in MD or val.replace("-", " ") in MD
                                  or val.split("-",1)[-1].replace("-"," ") in MD)
        gate(ok, f"{lbl} ({val})", "GRAPH")
    gate("frame" in MD.lower() and "calibration" in MD.lower(),
         "record carries the self-conviction (frame-entailed null, missing calibration) prominently",
         "GRAPH")
    gate("Born measure" in MD and "CLPW" in MD, "record carries both unopened doors", "GRAPH")
    gate("SUPPORTED" in MD and ("capped" in MD.lower()),
         "record carries the SUPPORTED cap on the differential record", "GRAPH")
else:
    print("  [ -- ] record not yet written")

print(f"\nBATTERY: {N-len(FAILS)}/{N}" + (f"  FAILURES: {FAILS}" if FAILS else ""))
print(f"CONVERGENCE (from journal): {CONV} | GRUT (from journal): {GRUT}")
print("W-0 -- chamber verdicts reported, NOT banked. Register unmodified. Fences unmoved.")
sys.exit(1 if FAILS else 0)
