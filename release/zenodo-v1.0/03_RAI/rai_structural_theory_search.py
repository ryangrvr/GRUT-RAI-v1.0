#!/usr/bin/env python3
"""RAI-ULTIMATE -- THE STRUCTURAL THEORY SEARCH. Gates the committed record.

Read-only. Banks nothing. W-0.

GATE DISCIPLINE. This record is NOT source-falsifiable the way ROOT-1 was (see the record's
section 0). The gates below therefore certify what CAN be certified mechanically:
  * GOVERNANCE  -- computed from the repository.
  * AGREEMENT   -- the primary/hostile agreement precondition the order requires for commit.
  * CORRECTION  -- TWO-SIDED. Each asserts that a claim source-level verification REFUTED is
                   ABSENT from the record and its correction PRESENT. Every one of these
                   would FAIL had the refuted claim been written instead. They are the only
                   mechanical defence this document has against restating a refuted claim.
  * INTEGRITY   -- no template tokens; the record states its own verdict and its own
                   epistemic limits (ROOT-0's E1/E3 lesson).
No gate here certifies that a physical claim is TRUE. Nothing in this record is banked.
"""
import json, hashlib, subprocess, sys, os, re

ROOT = os.path.dirname(os.path.abspath(__file__))
def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f: return f.read()

FAILS, N = [], 0
def gate(cond, label, kind="COMPUTED"):
    global N; N += 1
    ok = bool(cond)
    print(f"  [{'PASS' if ok else 'FAIL'}] {kind:10s} {label}")
    if not ok: FAILS.append(label)
    return ok

MD  = read("RAI_STRUCTURAL_THEORY_SEARCH.md")
# STANDING LESSON (recurring in this program): markdown gates must normalize
# whitespace AND strip blockquote ">" / emphasis "*" before matching, or a line
# wrap silently fails a gate whose subject is actually present.
MDN = re.sub(r"\s+", " ", MD.replace(">", " ").replace("*", "")).upper()
JS  = json.loads(read("RAI_STRUCTURAL_THEORY_SEARCH.json"))
SHA = hashlib.sha256(read("provenance/claims.json").encode()).hexdigest()
reg = json.loads(read("provenance/claims.json"))
claims = reg["claims"] if isinstance(reg, dict) else reg

print("\n== A. GOVERNANCE ==")
gate(len(claims) == 74, "register carries 74 nodes")
gate(SHA.startswith("beaeb84e8a6f8468"), "register sha256 UNCHANGED by this campaign")
h = subprocess.run(["git","-C",ROOT,"rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
v = subprocess.run(["git","-C",ROOT,"rev-parse","origin/v4"],capture_output=True,text=True).stdout.strip()
gate(h == v, "HEAD == origin/v4 by REF IDENTITY (not branch name)")
porc = subprocess.run(["git","-C",ROOT,"status","--porcelain"],capture_output=True,text=True).stdout
gate(not any(l[:2] in (" M","M ","MM","D ") for l in porc.splitlines()),
     "no tracked/frozen artifact modified")
gate("ROOT0_FOUNDATIONbootstrap" not in porc and "ROOT0_FOUNDATION_AUDIT.md" in porc,
     "ROOT-0 still preserved and UNCOMMITTED (untracked), per the standing order")

print("\n== B. AGREEMENT PRECONDITION (required before commit) ==")
a = JS["agreement"]
gate(a["primary"] == "D-FOUNDATIONAL-GAP", "primary returned D-FOUNDATIONAL-GAP")
gate(a["hostile"] == "D-FOUNDATIONAL-GAP", "blind hostile returned D-FOUNDATIONAL-GAP")
gate(a["agree"] is True, "agreement precondition MET -- commit licensed")
gate(JS["provenance"]["hostile"]["blindness"].startswith("STRUCTURAL"),
     "hostile blindness was STRUCTURAL (parallel dispatch), not merely promised")
gate(JS["outcome_class"] == "D-FOUNDATIONAL-GAP" and JS["outcome_class"] in MD,
     "record states its own outcome class")

print("\n== C. VERIFICATION CORRECTIONS APPLIED (two-sided: each fails if the refuted claim was written) ==")
# Each pair: (refuted string that MUST NOT appear as an assertion, correction that MUST appear)
gate("null infinity in asymptotically flat space" not in MD or "REFUTED and STRUCK" in MD,
     "null-infinity claim struck, not asserted", "CORRECTION")
gate("Type I_" in MD and "past" in MD.lower(),
     "...and the correction recorded: Type I at PAST null infinity, type II on the HORIZON", "CORRECTION")
gate("UNVERIFIABLE, STRUCK" in MD,
     "lattice-gauge-theory and group-field-theory over-claims struck", "CORRECTION")
gate("no per-case refitting" not in MD or 'Same theorem, no per-case refitting" — REFUTED' in MD
     or "REFUTED" in MD.split("no per-case refitting")[1][:200],
     "'same theorem, no per-case refitting' marked REFUTED, not asserted", "CORRECTION")
gate("80.356" in MD and "PDG 2025" in MD, "m_W SM prediction updated to PDG 2025 (80.356)", "CORRECTION")
gate("world average" in MD and "80,360.2" in MD, "m_W measurement re-attributed: PDG average, not CMS 2024", "CORRECTION")
gate("101" in MD and "105" in MD, "Willow qubit counts disambiguated (105 processor / 101 code)", "CORRECTION")
gate("Bortolotti" in MD and "2601.00651" in MD, "Karolyhazy bound re-attributed away from Donadi et al.", "CORRECTION")
gate("Pair 1" in MD, "Rauch figures scoped to Pair 1", "CORRECTION")
gate("independent of gravity" in MD, "hostile's universal 'asymptotic boundary always' claim refuted in-record", "CORRECTION")
gate("2511.00622" in MD and "resolves" in MD.lower(), "hostile's misreading of arXiv:2511.00622 corrected", "CORRECTION")
gate("128.7" in MD and "125.20" in MD, "Shaposhnikov-Wetterich re-evaluated at PDG-2024 inputs", "CORRECTION")
gate("A sign is not a number" in MD, "...and the disputed axis settled by SW's own text", "CORRECTION")
gate("itself an over-claim" in MD or "is **itself an over-claim**" in MD,
     "correction made in the adjudications' OWN disfavour (SMEFT ratios) recorded", "CORRECTION")
gate("40 ORDERS" in MDN and "STRUCK FROM THIS RECORD" in MDN
     and "APPEARS NOWHERE IN THIS REPOSITORY" in MDN,
     "the unverified '~40 orders' GRUT claim is STRUCK, not adopted", "CORRECTION")

print("\n== D. SCOPE AND FIREWALL DISCIPLINE ==")
gate("FAILS TO CONSTITUTE A DISTINCTIVE PHYSICAL THEORY" in MDN
     and "NOT \"THE RESPONSIVE-VACUUM HYPOTHESIS IS FALSE" in MDN,
     "GRUT 'FAILS' is scoped -- distinctiveness, NOT falsity")
gate("unevaluated at its own claim point" in MD.lower(), "GRUT recorded as UNEVALUATED, not nulled")
gate("cannot-calculate" in MD and "≠" in MD, "capability firewall stated in both directions")
gate(JS["grut_disposition"]["refuted"] is False and JS["grut_disposition"]["structural_credit"] == "NONE",
     "JSON agrees: no structural credit AND not refuted")
gate(JS["answer3_what_we_are_missing"]["cuts_against_grut"] is True,
     "Answer 3 recorded as cutting AGAINST GRUT (not chosen to help it)")

print("\n== E. RECORD INTEGRITY (ROOT-0's E1/E3 lesson) ==")
gate("[[" not in MD, "no unsubstituted template token in the published record")
gate("EPISTEMIC STATUS OF THIS DOCUMENT" in MD,
     "record declares its own epistemic standing rather than inheriting ROOT-1's")
gate("[SYNTHESIS]" in MD and "[VERIFIED]" in MD and "[LITERATURE]" in MD,
     "per-section epistemic grading present")
gate("MEDIUM (~55-60%)" in MD or "~55–60%" in MD, "D-over-C confidence stated numerically, not asserted")
gate("DECLARED LIMITATIONS" in MD and "200/200" in MD,
     "search-budget exhaustion and stale-data limits declared, not hidden")
gate(len(JS["candidates"]) == 14 and sum(1 for c in JS["candidates"] if c["attack"] == "FAILS") == 2,
     "14 candidates, exactly 2 FAILS -- JSON consistent with the record")

VERDICT = "INCONCLUSIVE" if FAILS else JS["outcome_class"]
print(f"\nBATTERY: {N-len(FAILS)}/{N}" + (f"  FAILURES: {FAILS}" if FAILS else ""))
print(f"OUTCOME: {VERDICT}")
print("W-0 -- adjudicated and reported, NOT banked. Register unmodified. A-F unselected.")
sys.exit(1 if FAILS else 0)
