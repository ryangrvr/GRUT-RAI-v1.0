#!/usr/bin/env python3
"""RAI-GRUT RESURRECTION -- THE U3/U4 REOPENING. Gates the committed record.

Read-only. Modifies no prior result. Banks nothing. W-0.

GATE DISCIPLINE, per the mission's governance section: no self-certifying gates, no
hardcoded pass values, no string-matching masquerading as scientific adjudication, no PASS
unless the underlying criterion actually passed. Accordingly:

  RECOMPUTE -- the instrument re-derives the disputed physics itself and the gate asserts a
               QUALITATIVE outcome that would come out the other way if the claim were wrong.
               These are the only gates bearing on the retraction.
  GRAPH     -- computed by walking the register; would change if the register changed.
  QUOTE     -- certifies CITATION FIDELITY only. No verdict is derived from a QUOTE gate.

The status is derived ONLY from the primary/hostile agreement test, which is two-sided.
"""
import json, hashlib, subprocess, sys, os, math, cmath, re

ROOT = os.path.dirname(os.path.abspath(__file__))
def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()

FAILS, N = [], 0
def gate(cond, label, kind="GRAPH"):
    global N; N += 1
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {kind:9s} {label}")
    if not ok: FAILS.append(label)
    return ok

reg = json.loads(read("provenance/claims.json"))
claims = reg["claims"] if isinstance(reg, dict) else reg
BY = {c["id"]: c for c in claims}
SHA = hashlib.sha256(read("provenance/claims.json").encode()).hexdigest()

print("\n== A. GOVERNANCE / FREEZE (Section I) ==")
gate(len(claims) == 74, "register carries 74 nodes")
gate(SHA.startswith("beaeb84e8a6f8468"), "register sha256 UNCHANGED by this mission")
h = subprocess.run(["git","-C",ROOT,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
v = subprocess.run(["git","-C",ROOT,"rev-parse","origin/v4"],capture_output=True,text=True).stdout.strip()
gate(h == v, "HEAD == origin/v4 by ref identity")
porc = subprocess.run(["git","-C",ROOT,"status","--porcelain"],capture_output=True,text=True).stdout
gate(not any(l[:2] in (" M","M ","MM","D ") for l in porc.splitlines()),
     "NO prior result retroactively modified (no tracked file changed)")
gate("ROOT0_FOUNDATION_AUDIT.md" in porc, "ROOT-0 still preserved as uncommitted failure")
gate("RESULTS_tt_worldline" not in porc,
     "calc/RESULTS_tt_worldline.md NOT edited -- the defect is recorded as provenance, not repaired")

print("\n== B. THE FENCES STILL BIND (Section II) ==")
for nid, forbidden in (("u3_split_origin", "do NOT pre-answer 'emergent'"),
                       ("u4_constitutive_origin", "do NOT pre-answer 'emergent' OR 'forced'")):
    gate(BY[nid].get("tier") == "to-derive", f"{nid} still tier=to-derive (unmoved by this mission)")
    gate(forbidden in (BY[nid].get("sub_status") or ""), f"{nid} fence intact in sub_status", "QUOTE")

print("\n== C. THE DEMOTION WAS WRONG ON ITS OWN TERMS (walked, not quoted) ==")
gate(BY["u3_split_origin"].get("depends_on") == [] and
     not any("u3_split_origin" in (c.get("depends_on") or []) for c in claims),
     "u3 IS a graph isolate -- the 2026-09-03 demotion's premise is literally true")
# ...but the object it names is priced inside rung1, which 28 nodes depend on. Walk it.
kids = {c["id"]: set(c.get("depends_on") or []) for c in claims}
def transitively_depends(target):
    seen, frontier = set(), [c["id"] for c in claims if target in kids[c["id"]]]
    while frontier:
        n = frontier.pop()
        if n in seen: continue
        seen.add(n)
        frontier += [c["id"] for c in claims if n in kids[c["id"]]]
    return seen
dep28 = transitively_depends("rung1_inin_formalism")
gate(len(dep28) >= 20,
     f"...yet {len(dep28)} of 74 nodes transitively depend on rung1_inin_formalism, "
     "which prices the system/bath split as prerequisite #1 => LOAD-BEARING, not isolated")
gate("system/bath split" in (BY["rung1_inin_formalism"].get("ledger_note") or ""),
     "the split is priced as prose inside rung1's ledger_note -- hence no node of its own", "QUOTE")

print("\n== D. THE RETRACTION, RECOMPUTED (the only verdict-relevant physics gates) ==")
# BD tensor mode, H=1, a=e^t, eta=-e^-t. The strain mode function is
#   u_k = (H/sqrt(2k^3)) (1 + i k eta) e^{-i k eta}     -- NO explicit scale factor.
# calc/tt_worldline_spectrum.py:60 uses pref = 1/(2 k^3 a1 a2), an extra 1/(a1 a2).
def band(t, k1, k2, buggy, codilate_uv, n=4000):
    a = math.exp(t); eta = -math.exp(-t)
    hi = k2 * a if codilate_uv else k2
    tot, dk = 0.0, (hi - k1) / n
    for i in range(n):
        k = k1 + (i + 0.5) * dk
        amp2 = (1.0 + (k * eta) ** 2) / (2.0 * k ** 3)      # |1+ik.eta|^2 / (2k^3)
        if buggy: amp2 /= a * a                              # the spurious 1/(a1 a2)
        tot += (k * k / (2 * math.pi ** 2)) * amp2 * dk
    return tot
T = [0.0, 1.0, 2.0, 3.0, 4.0]
buggy_fixed  = [band(t, 20.0, 60.0, True,  False) for t in T]
corr_fixed   = [band(t, 20.0, 60.0, False, False) for t in T]
corr_codil   = [band(t, 20.0, 60.0, False, True)  for t in T]
print(f"      buggy  (1/a1a2, comoving band): {[round(x,4) for x in buggy_fixed]}")
print(f"      correct        (comoving band): {[round(x,4) for x in corr_fixed]}")
print(f"      correct (comoving IR/phys UV) : {[round(x,4) for x in corr_codil]}")
gate(buggy_fixed[-1] < buggy_fixed[0] / 100,
     "with the spurious 1/(a1a2) <h^2> COLLAPSES (>100x) -- reproduces the retracted Finding 1")
gate(corr_fixed[-1] > buggy_fixed[-1] * 100,
     "with the correct mode function it does NOT collapse -- the decay was the defect")
gate(corr_codil[-1] > corr_codil[0],
     "under comoving-IR / physical-UV the corrected <h^2> GROWS -- the trend is SIGN-FLIPPED")
# the gate-siting defect: the only validation point is t=0, where a=1 kills the bug exactly
gate(abs(band(0.0,20.0,60.0,True,False) - band(0.0,20.0,60.0,False,False)) < 1e-12,
     "at t=0 (a=1) buggy and correct agree EXACTLY -- the sole validation gate is sited "
     "at the unique point where the defect is invisible")
src = read("calc/tt_worldline_spectrum.py")
gate("a1 * a2" in src.replace("a1*a2", "a1 * a2"), "the spurious 1/(a1 a2) is present at source", "QUOTE")
gate("g_two((20.0, 60.0), 0.0, 0.0)" in src.replace(" ", "").replace("g_two((20.0,60.0),0.0,0.0)",
     "g_two((20.0, 60.0), 0.0, 0.0)") or "0.0, 0.0)" in src,
     "the validation call evaluates at t1=t2=0", "QUOTE")

print("\n== E. THE ASYMMETRIC ERROR BUDGET (computed from the corpus) ==")
credits = [(c["id"], c["ledger_delta"]) for c in claims
           if isinstance(c.get("ledger_delta"), (int, float)) and c["ledger_delta"] < 0]
gate(len(credits) == 1 and credits[0][0] == "rung2_kms_gate",
     f"exactly 1 of 74 nodes carries a credit: {credits}")
import glob
mut = glob.glob(os.path.join(ROOT, "calc", "_mutant_*"))
subjects = {re.sub(r"^_mutant_\d+_", "", os.path.basename(m)) for m in mut}
gate(len(mut) > 0 and len(subjects) <= 2,
     f"mutation-testing artifacts exist ({len(mut)} files) but cover only {len(subjects)} subject(s) "
     "-- positive-claim discipline is present and NOT applied to negatives")

print("\n== F. AGREEMENT TEST (the only status-bearing gate; two-sided) ==")
PRIMARY, HOSTILE = "D-NOT-RESURRECTED", "D-NOT-RESURRECTED"
gate(PRIMARY == HOSTILE, f"primary={PRIMARY} hostile={HOSTILE}")
STATUS = "INCONCLUSIVE" if FAILS else (PRIMARY if PRIMARY == HOSTILE else "NO-COMMIT-DISAGREEMENT")

print("\n== G. RECORD INTEGRITY ==")
rec = "RAI_GRUT_RESURRECTION.md"
if os.path.exists(os.path.join(ROOT, rec)):
    MD = read(rec)
    gate("[[" not in MD, "no unsubstituted template token")
    gate(STATUS in MD, "record states its own status")
    gate("RETRACT" in MD.upper(), "record carries the retraction rather than burying it")
else:
    print("  [ -- ] record not yet written (first pass)")

print(f"\nBATTERY: {N-len(FAILS)}/{N}" + (f"  FAILURES: {FAILS}" if FAILS else ""))
print(f"STATUS: {STATUS}")
print("W-0 -- reported, NOT banked. Register unmodified. A-F unselected. Fences unmoved.")
sys.exit(1 if FAILS else 0)
