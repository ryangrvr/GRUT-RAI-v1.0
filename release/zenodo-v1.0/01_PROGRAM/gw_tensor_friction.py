#!/usr/bin/env python3
"""calc/gw_tensor_friction.py -- GRUT's induced cosmological tensor friction Gamma_T:
THE CLOSURE COMPUTATION, built to calc/SPEC_gw_tensor_friction.md (2026-08-22) under
GRUT_PREDICTION_GATE_GAMMA_T.md (2026-09-06, commit 2116251).

CLOCK DECLARATION (SPEC section 4 / keystone C5): single FRW COSMIC clock throughout.
Every rate below is d/dt_cosmic; no static-Killing or e-fold quantity is imported.

CHANNEL DECLARATION (SPEC Q-D): the observable is STANDARD-SIREN AMPLITUDE
(d_L^GW / d_L^EM). No dephasing number is re-derived; the 22-62-order dephasing
statements in the seven downstream documents are untouched (SPEC section 7).

VERDICT DISCIPLINE (the de-pinned standard): the SPEC section-5 outcome printed at the
end is COMPUTED from statuses extracted out of provenance/claims.json and
PHYSICS_LEDGER/ROOT1_KERNEL_ORIGIN.md at runtime. No outcome string is pre-selected;
if the register's sector fork is ever re-booked FORCED/derived, this file routes
differently. Nothing here banks; claims.json is read-only to this file.

Convention note (declared, SPEC trap 2): the Tier-4 kernel coefficients are used per
unit Mbar_P^-2 (reduced Planck mass); an 8pi-class convention slip moves the licensed
number by <~1.5 orders against a ~62-order verdict margin -- the verdict is
convention-slop-insensitive, and this is reported (not gated) below.

SPEC trap dispositions (traps 1 and 3, stated on the file's face per the 2026-09-06
verification): trap 1 (transplanted forms) -- the only borrowed closed forms are the
register's OWN Tier-4 kernel and two-scale ansatz; the kernel's defining coefficient
relation (13/480)/(3/1280) = 104/9 is asserted exactly (it IS the ROOT-1 O1 identity),
both coefficients are extraction-checked against the kr_contract_retarded_tier4 node at
runtime, and the flat-contract scope is carried via the [1 + (104/9)(H0/w)^2] validity
term the kernel itself supplies -- no external-background transplant occurs. Trap 3
(magnitude-only comparison) -- no two candidate solutions sharing a magnitude are
compared here; horn separation is by chromaticity CLASS (w^3 vs achromatic), and the
alpha_M separation is category-fenced (gate doc R4), not adjudicated by magnitude.
"""
import json, math, os, re, sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# ---------------------------------------------------------------- constants (sourced)
C     = 2.99792458e8                       # m/s
MPC   = 3.0856775814913673e22              # m
HBAR  = 1.054571817e-34
G     = 6.67430e-11
H0_KMSMPC = 67.4                           # Planck 2018 TT,TE,EE+lowE+lensing
H0    = H0_KMSMPC * 1e3 / MPC              # s^-1  (~2.184e-18)
OM    = 0.31; OL = 1.0 - OM                # same background as wz_dark_energy.py
OMEGA_P    = math.sqrt(C**5 / (HBAR * G))          # Planck angular frequency ~1.855e43
OMEGA_PBAR = math.sqrt(C**5 / (8*math.pi*HBAR*G))  # reduced ~3.70e42 (Mbar_P c^2/hbar)
SLOT_BOUND_OVER_H0 = 3.0                   # "few x H0", arXiv:2507.03103 (shared slot)
F_BAND = [10.0, 100.0, 1024.0]             # Hz, as in gw_dissipation_bounds.py

# Tier-4 kernel absorptive coefficients (K_R contract; Im L = pi, mu-independent)
C4 = Fraction(3, 1280)                     # omega^4 log coefficient / pi^2
C2H = Fraction(13, 480)                    # H^2 omega^2 log coefficient / pi^2

# Booked two-scale ansatz inputs (statuses attached; SPEC Q-B/Q-C and section 4)
B_STAKED = 0.4          # staked illustrative (wz_dark_energy.py eps; B==eps UNVERIFIED)
B_CONF   = 2.4e-4       # implied by the conformalon epoch-free rate leg (SPEC Q-B)
A_UV     = 1.0          # declared; the UV amplitude is equally unpinned
OMEGA_C  = {            # three in-corpus values, 39.6-order span (SPEC section 4)
    "2pi*689 rad/s (in-corpus)": 2*math.pi*689.0,
    "1e40*H0 (hand-set, wz_dark_energy.py:61)": 1e40*H0,
    "Planck frequency": OMEGA_P,
}

def fail(msg):
    print("GATE-FAIL:", msg); sys.exit(1)

# ================================================================ 0 . register reads
# Dynamic needles: statuses are EXTRACTED, and the verdict computed from them.
claims_raw = open(os.path.join(ROOT, 'provenance', 'claims.json')).read()
claims = json.load(open(os.path.join(ROOT, 'provenance', 'claims.json')))
cl = claims['claims'] if isinstance(claims, dict) and 'claims' in claims else claims
cl = cl if isinstance(cl, list) else list(cl.values())
byid = {c.get('id'): c for c in cl}

def node_text(nid):
    c = byid.get(nid)
    if c is None: fail(f"register node {nid} not found")
    return json.dumps(c)

# Sector-fork adjudication inputs (Q-A). We do NOT search for a wanted verdict; we
# extract the forced-vs-chosen adjudication each node itself records.
def forced_or_chosen(nid):
    t = node_text(nid)
    has_chosen = bool(re.search(r'VERDICT = CHOSEN|CHOSEN AT THE ENUMERATED FRAME/ORDER', t))
    has_forced = bool(re.search(r'VERDICT = FORCED|FORCED AT THE ENUMERATED FRAME/ORDER', t))
    if has_chosen and not has_forced: return "CHOSEN"
    if has_forced and not has_chosen: return "FORCED"
    return "UNADJUDICATED"

ptt_status  = forced_or_chosen('p_tt_ansatz')
frame_status = forced_or_chosen('eft_operator_basis')
tau2_inserted = bool(re.search(r'inserted, un-sourced', node_text('rung7_wz')))
rung7_tier = byid['rung7_wz'].get('tier')

root1_path = os.path.join(ROOT, 'PHYSICS_LEDGER', 'ROOT1_KERNEL_ORIGIN.md')
root1 = open(root1_path).read() if os.path.exists(root1_path) else ""
ir_unaskable = 'UNASKABLE' in root1

# Well-formedness gates (assert structure, never a verdict):
if ptt_status == "UNADJUDICATED": fail("p_tt_ansatz carries no forced-vs-chosen adjudication")
if frame_status == "UNADJUDICATED": fail("eft_operator_basis carries no frame-level adjudication")
if rung7_tier is None: fail("rung7_wz has no tier")
exact_ratio = C2H / C4
if exact_ratio != Fraction(104, 9): fail(f"(13/480)/(3/1280) != 104/9 (got {exact_ratio})")
# Extraction-success gate: the hard-coded Tier-4 coefficients must appear verbatim in the
# banked node, so a re-banked coefficient cannot go stale silently (verification finding).
kr_txt = node_text('kr_contract_retarded_tier4')
if '3/1280' not in kr_txt or '13/480' not in kr_txt:
    fail("Tier-4 coefficients not found verbatim in kr_contract_retarded_tier4 -- re-check")

print("=" * 86)
print("GAMMA_T -- THE CLOSURE COMPUTATION   (clock: single FRW cosmic; channel: siren amplitude)")
print("=" * 86)

# ================================================================ 1 . Q-A (dominates)
print("\n(Q-A) THE SECTOR QUESTION -- settled from the booked family, or not:")
print(f"    p_tt_ansatz (TT-only projector)          : {ptt_status}  (tier {byid['p_tt_ansatz'].get('tier')})")
print(f"    eft_operator_basis (admissible family)   : {frame_status}  (tier {byid['eft_operator_basis'].get('tier')})")
print(f"    rung7_wz two-scale commitment            : tier {rung7_tier}; tau_2 inserted un-sourced: {tau2_inserted}")
print(f"    ROOT-1 IR standing (omega <~ 3.4H)       : {'UNASKABLE (O1-O4)' if ir_unaskable else 'not on record'}")

# The computed adjudication: the sector question is settled by the booked family only if
# some booked node DERIVES the channel assignment (a FORCED verdict). A CHOSEN verdict
# on every booked level means the assignment is a choice, and the two horns disagree.
sector_settled = (ptt_status == "FORCED") or (frame_status == "FORCED")
if sector_settled:
    qa = "SETTLED"
    print("    => a booked node derives the channel assignment; horns collapse to one.")
else:
    qa = "UNDECIDABLE-FROM-BOOKED-FAMILY"
    print("    => every booked adjudication returns CHOSEN: the friction-carrying channel")
    print("       assignment is a projector CHOICE at every booked level, the two horns of")
    print("       SPEC section 3 disagree, and nothing booked selects between them.")

# ================================================================ 2 . horn (a): licensed
print("\n(HORN a) THE LICENSED, PARAMETER-FREE ENTRY (Tier-4 derived kernel, omega >> H):")
print("    Gamma_T(w) = (3/1280pi) * w^3/Mbar_P^2 * [1 + (104/9) (H0/w)^2]   (Im L = pi:")
print("    the absorptive part is mu-INDEPENDENT -- no scheme slot enters the friction).")
coeff = float(C4) / math.pi
rows = []
for f in F_BAND:
    w = 2*math.pi*f
    hcorr = float(exact_ratio)*(H0/w)**2      # printed directly: 1+hcorr == 1.0 in double
    gam = coeff * w**3 / OMEGA_PBAR**2 * (1.0 + hcorr)
    rows.append((f, w, gam, gam/H0, hcorr))
    print(f"    f = {f:7.1f} Hz : Gamma_T = {gam:.3e} s^-1 = {gam/H0:.3e} * H0"
          f"   (H^2 corr term {hcorr:.1e}, below double precision)")
g10, g1024 = rows[0][2], rows[2][2]
scaling = (g1024/g10) / (F_BAND[2]/F_BAND[0])**3
if abs(scaling - 1.0) > 1e-6: fail(f"chromaticity check: w^3 scaling off by {scaling}")
gam100_over_H0 = rows[1][3]
orders_below = math.log10(SLOT_BOUND_OVER_H0 / gam100_over_H0)
print(f"    vs the shared-slot bound few*H0: {orders_below:.1f} ORDERS BELOW at 100 Hz.")
print(f"    Convention slop (8pi-class, <~1.5 orders) vs margin ({orders_below:.0f} orders):")
slop_orders = math.log10(8*math.pi)
# REPORT, never gate: a thin margin would be a reportable result, not a malformed run
# (a fail() here was the pass-label pattern in miniature; caught pre-commit 2026-09-06).
if orders_below - slop_orders >= 50:
    print(f"    insensitive (slop {slop_orders:.2f} orders; margin holds by >{orders_below - slop_orders:.0f}).")
else:
    print(f"    CAUTION: margin ({orders_below:.1f} orders) is within ~50 orders of the slop;")
    print(f"    the insensitivity claim is WEAKENED to convention-dependent -- so reported.")

# ================================================================ 3 . horn (b): conditional
print("\n(HORN b) CONDITIONAL EXHIBITS -- NOT banked, NO headline; every line depends on")
print("    tau_2 (INSERTED +2), B (STAKED), B==eps (UNVERIFIED), sector (CHOSEN):")
print("    achromatic limit Gamma_T -> B*H0/2 for w*tau_2 >> 1  [SPEC section 1].")

def lookback_H0(z):    # H0 * t_lookback(z), flat LCDM, trapezoid
    n = 4000; s = 0.0
    for i in range(n):
        z1 = z*i/n; z2 = z*(i+1)/n
        f1 = 1.0/((1+z1)*math.sqrt(OM*(1+z1)**3+OL))
        f2 = 1.0/((1+z2)*math.sqrt(OM*(1+z2)**3+OL))
        s += 0.5*(f1+f2)*(z2-z1)
    return s

ZREF = 0.5
h0tl = lookback_H0(ZREF)
print(f"    amplitude channel (Q-D): Xi(z) = d_L^GW/d_L^EM = exp(+(Gamma_T/2)*t_lookback);")
print(f"    H0*t_lookback(z={ZREF}) = {h0tl:.4f}")
for name, Bval in [("B = 0.4 (staked)", B_STAKED), ("B ~ 2.4e-4 (conformalon leg)", B_CONF)]:
    gT = Bval/2.0   # in units of H0
    xi = math.exp(0.5*gT*h0tl)
    print(f"    {name:32s}: Gamma_T = {gT:.2e}*H0 ; Xi(z={ZREF}) - 1 = {xi-1.0:.2e}")
print("    COMPOSED (the SPEC's owed composition): the two live B values differ by "
      f"{math.log10(B_STAKED/B_CONF):.1f} orders")
print("    and nothing on the record selects between them; the induced siren-amplitude")
print("    effect spans 'percent-level at z~0.5' to 'invisible' ACROSS ONE STAKED CONSTANT.")
print("    MATCH-TEMPTATION FENCE (SPEC trap 4): B=0.4 landing inside the slot bound is a")
print("    staked amplitude near a SHARED-slot bound -- evidential weight ZERO.")
print("    (Q-C) B and eps are carried as SEPARATE symbols; the identification is unverified")
print("    and no line above uses it.")

print("\n    w_c SENSITIVITY (SPEC section 4; crossover w_x = sqrt(B*H0*w_c/A), A=1 declared):")
xs = {}
for name, wc in OMEGA_C.items():
    wx = math.sqrt(B_STAKED*H0*wc/A_UV)
    xs[name] = wx
    print(f"      w_c = {name:42s}: w_x = {wx:.3e} rad/s = {wx/(2*math.pi):.3e} Hz")
wx_hand = xs["1e40*H0 (hand-set, wz_dark_energy.py:61)"]; wx_pl = xs["Planck frequency"]
ratio_check = (wx_pl/wx_hand) / math.sqrt(OMEGA_P/(1e40*H0))
if abs(ratio_check - 1.0) > 1e-9: fail("crossover sqrt(w_c) scaling violated")
print(f"      span across the three w_c: {math.log10(max(xs.values())/min(xs.values())):.1f} orders"
      " -- an unpinned constant; enters no headline (SPEC section 4 obligation).")

# ================================================================ 4 . verdict (computed)
print("\n" + "=" * 86)
if qa == "SETTLED":
    # Loud fail-forward (verification finding): this closure instrument does NOT
    # adjudicate the settled branch -- PASS / FAIL-BUT-INFORMATIVE / CLOSES-THE-QUESTION
    # need a new run built against the booked derivation. No SPEC outcome is emitted.
    verdict = ("SECTOR-SETTLED: closure instrument out of scope -- a new run against the "
               "booked derivation is required before any SPEC section-5 outcome is emitted")
else:
    verdict = "REFUSE"
print(f"SPEC section-5 OUTCOME (computed from extracted statuses): {verdict}")
if verdict == "REFUSE":
    # The obstruction stack is ASSEMBLED from the runtime-extracted flags (verification
    # finding: a static narrative could go stale against its own Q-A printout).
    obs = []
    if ptt_status == "CHOSEN":
        obs.append("the TT-only channel assignment is CHOSEN, not forced (p_tt_ansatz\n"
                   "        boundary_condition, five-angle interrogation, unanimous)")
    if frame_status == "CHOSEN":
        obs.append("the admissible-family frame-level adjudication is also CHOSEN\n"
                   "        (eft_operator_basis boundary_condition)")
    if tau2_inserted:
        obs.append("the friction-carrying tau_2 pole is an INSERTED, un-sourced commitment\n"
                   "        (rung7_wz, +2 of its +3), i.e. horn (b) is FAIL-BUT-INFORMATIVE-shaped\n"
                   "        BEFORE the sector question is even reached")
    if ir_unaskable:
        obs.append("the region where that pole lives (omega <~ 3.4 H) is UNASKABLE at current\n"
                   "        declarations (ROOT-1 section 3, obstructions O1-O4) -- the derivation that\n"
                   "        would settle Q-A cannot currently be posed")
    roman = ["(i)  ", "(ii) ", "(iii)", "(iv) "]
    print("""
The sector question (Q-A) CANNOT be settled from the booked family. The obstruction,
named per the SPEC's standing guard ('my machinery cannot in principle produce this,
and here is which obstruction applies'):""")
    for tag, o in zip(roman, obs):
        print(f"  {tag} {o};")
    print("""WHAT THE REFUSE DOES AND DOES NOT DO:
  - It terminates the SPEC's question cleanly (SPEC section 5, REFUSE clause).
  - The pre-registered register question -- 'does the local memory scale connect
    parameter-free?' -- is answered NO on the licensed record: the only parameter-free
    entry is horn (a), ~62 orders below the shared-slot bound (NO EFFECT); every
    observable-sized route runs through inserted/staked/choice-dependent inputs.
  - SIGNATURE_AUDIT's gate-to-readmit is closed as a COMPUTED REFUSAL: the <=1e-21
    figures stay un-readmitted; nothing banks.
  - EDIT 1's conditional marker is NOT finalised (that required a scalar-only Q-A
    answer, which this REFUSE is not).
  - claims.json untouched; TT quarantine and Class-A suspension untouched; the
    22-62-order dephasing statements untouched (SPEC section 7).""")
print("=" * 86)
print("ALL GATES PASSED (well-formedness + arithmetic identities + scaling checks;")
print("no gate asserts which verdict passes).")
