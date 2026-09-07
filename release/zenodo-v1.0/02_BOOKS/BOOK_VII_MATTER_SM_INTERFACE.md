# BOOK VII — MATTER AND THE STANDARD MODEL INTERFACE

> **WORKING DRAFT** — part of the GRUT working corpus; statuses per `books/CORPUS_CHARTER.md`;
> subject to chapter-by-chapter audit; nothing here banks.

**GRUT Books — Working Edition v1.0** · D. Ryan Grover · 2026-09-07 · release `zenodo-v1.0` · Markdown is the authoritative source; the PDF is generated from it. Drafted from the frozen record by the RAI builder (Claude, Anthropic) under owner direction — this edition is a publishing pass only: formatting, navigation, and metadata; no claim strengthened or weakened for publication.

## Contents

- [1 · The headline, stated first](#1--the-headline-stated-first)
- [2 · Where matter actually enters the frozen record](#2--where-matter-actually-enters-the-frozen-record)
  - [2.1 Matter as bath content: one structural selection](#21-matter-as-bath-content-one-structural-selection)
  - [2.2 The matter-loop prohibition: absence as discipline](#22-the-matter-loop-prohibition-absence-as-discipline)
  - [2.3 The trace-anomaly α leg: the one place SM-type field content touches a coefficient](#23-the-trace-anomaly-α-leg-the-one-place-sm-type-field-content-touches-a-coefficient)
  - [2.4 Yukawa, but not flavor](#24-yukawa-but-not-flavor)
  - [2.5 The archived strong-CP conjecture: uncertified lineage](#25-the-archived-strong-cp-conjecture-uncertified-lineage)
  - [2.6 The register's absence bookkeeping itself](#26-the-registers-absence-bookkeeping-itself)
- [3 · The electroweak sector as it actually appears: the vacuum cluster](#3--the-electroweak-sector-as-it-actually-appears-the-vacuum-cluster)
- [4 · What the program's external audit says about the Standard Model — clearly not GRUT content](#4--what-the-programs-external-audit-says-about-the-standard-model--clearly-not-grut-content)
- [5 · The absence map proper: what a constitutive account would have to supply](#5--the-absence-map-proper-what-a-constitutive-account-would-have-to-supply)
- [Sources drawn from](#sources-drawn-from)
- [Gaps in this book](#gaps-in-this-book)

---

*Book VII of X. Electroweak physics, QCD, the Higgs sector, flavor, neutrinos, dark matter,
baryogenesis, and the question of how matter couples to the responsive vacuum. The reader
should know the shape of this book before entering it: most of this sector has **no GRUT
account on the record**, and the record itself established that absence by systematic
search rather than by neglect. This book's chief scientific content is therefore an
**absence map** — what exists (little), with its real status; what does not exist, stated
plainly; and what a constitutive-relational account of each topic would minimally have to
supply, so that the absence is legible rather than vague. Per the charter, an absence map
is valid content; padding it would violate the owner's directive. This book is accordingly
shorter than its siblings.*

---

## 1 · The headline, stated first

The canonical status table carries one entry that governs almost everything in this book's
scope:

> **STATUS: UNMAPPED** — flavor, strong-CP, neutrino masses, dark matter, baryogenesis
> (canonical table item 22; source: `books/CORPUS_CHARTER.md`).

This is not a shrug. The record *searched*. The FOREST Phase 11 expansion campaign
(2026-09-04, `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md`, instrument
`forest_phase11_mapping.py`, 50/50 battery, both adversarial legs run and their corrections
applied at source) resolved every named matter sector against the repository's actual text,
and its per-sector verdicts are finer-grained than a single "unmapped" — the distinctions
matter and are preserved here:

- **Flavor** — **MAPPED-ABSENT: no repository content.** Every occurrence of the word in
  the v4 working tree is colloquial ("generic-flavored," "authority-flavored"); no
  Yukawa/CKM/PMNS claim exists anywhere in the register or its prose.

  > **STATUS: UNMAPPED (established by search, not assumption; scope: the v4 working
  > tree)** — sector verdict MAPPED-ABSENT (source:
  > `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §A, §H).

- **Strong CP** — **MAPPED-ABSENT: no repository content.** The topic occurs in exactly
  one working-tree file, `provenance/merge_criterion.py`, and there only as a
  *methodological exemplar*: θ̄ and the electron Yukawa y_e serve as two indisputably
  separate Standard-Model inputs used to stress-test the merge-counting arithmetic (the D3
  "bundle theorem" defect — counting labels rather than real-parameter dimension lets
  anything merge on demand, θ̄ and y_e included). No physics claim about strong CP is made.

  > **STATUS: UNMAPPED (the sole occurrence is a counting exemplar, not physics)** —
  > (source: `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §A, §I;
  > `provenance/merge_criterion.py`).

- **Neutrinos** — **NOT-A-SECTOR.** Neutrinos appear in the working tree only as an
  **explicitly forbidden proxy**: the rung3 specialist brief bars "the literature-default
  minimally-coupled-massless-scalar proxy, neutrino loops, conformal-scalar loops, or any
  hand-inserted bath self-interaction" from the kernel derivation — a discipline fence
  against relocation, not a neutrino theory (see §2.2).

  > **STATUS: UNMAPPED (the only appearance is a prohibition)** — (source:
  > `SPECIALIST_BRIEF_rung3_spine.md`; `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §A).

- **Dark matter** — **RETIRED + DECLARED GAP.** An entire dark-matter substrate line
  existed in the superseded historical book and **died with it** — named in the
  superseding note rather than quietly dropped — and "dark-matter: particle content /
  non-gravitational sector" stands in the register's own `KNOWN_GAPS` list under the
  standing rule "absent != covered."

  > **STATUS: UNMAPPED, with retired history on its face** — the substrate line is model
  > history, not model content (sources: `handover/SUPERSEDING_NOTE.md`;
  > `docs/WHERE_IT_STOPS.md`; `provenance/coverage.py` KNOWN_GAPS).

- **Baryogenesis** — **DECLARED GAP.** In `KNOWN_GAPS` as "matter-antimatter asymmetry."
  No node, no observable, no mechanism.

  > **STATUS: UNMAPPED (declared gap)** — (source: `provenance/coverage.py` KNOWN_GAPS).

- **QCD** — **NOT-A-SECTOR.** QCD enters the record only as vacuum-energy condensate
  bookkeeping inside the vacuum-cluster map (§3 below) — a threshold magnitude, never a
  dynamics.

  > **STATUS: UNMAPPED as a dynamical sector (condensate bookkeeping only)** — (source:
  > `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §A; `VACUUM_CLUSTER_MAP.md` Ruling 2).

- **Coupling unification** — **RESOLVED NEGATIVE.** "Zero novel positive predictions — no
  channel examined produced one."

  > **STATUS: CLOSED (gate outcome — the examined channels produced nothing)** — (source:
  > `GRUT_II_What_Survived.md`; `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §A).

The strongest single in-tree statement of the whole situation is the emergence chain's own
matter link: "The Standard Model — its spectrum, its couplings, its three generations —
appears NOWHERE in the register … the chain's matter link is SILENT." The historical
constitution's assumed-list names "the SM spectrum" in prose, but **no register node books
it** — the silence is a registry gap as well as a physics gap.

> **STATUS: UNMAPPED (link status SILENT — no register node covers the matter link)** —
> (source: `EMERGENCE_CHAIN.md` §11).

One sharpening from Phase 11 deserves prominence: **flavor and strong-CP are *undeclared*
absences.** The register maintains an honest gap list (`KNOWN_GAPS`: quantum gravity,
black-hole interior, early universe, baryogenesis, dark matter), and flavor and strong-CP
are **not on it** — their absence was discovered by the mapping campaign, not previously
booked. The Phase 10 ruling made the consequence explicit: flavor and strong-CP "are not
in the register — unmapped, and ineligible for this ranking. If the program wants a fresh
candidate pool, mapping them is the prerequisite."

> **STATUS: UNRESOLVED (a bookkeeping gap the record has named but not repaired: two
> absences remain undeclared in `KNOWN_GAPS`)** — (sources:
> `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §H;
> `PHYSICS_LEDGER/FOREST_PHASE10_RESULT.md`).

## 2 · Where matter actually enters the frozen record

The absences above are the bulk of the story. What follows is the complete inventory —
so far as this book's search found — of where matter *does* touch the frozen record, with
each item's real status.

### 2.1 Matter as bath content: one structural selection

In the influence-functional architecture, matter appears exactly once as a physics input:
the **bath content** feeding the kernels is selected to be **massless relativistic modes**
— the simplest relativistic choice. That is the entire "matter sector" of the constitutive
mathematics: no gauge group, no chiral structure, no Higgs, no generations. The
distinctiveness ledger classifies this choice as "standard input," and its proviso — that
no second internal scale hides in the bath — is **undischarged**.

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — bath content chosen, not derived; the
> "no second internal scale" proviso undischarged)** — (source: `GRUT_MODEL_FRAMEWORK.md`
> §2).

### 2.2 The matter-loop prohibition: absence as discipline

The rung3 specialist brief makes the matter-absence partly *deliberate*: it explicitly
forbids inserting matter loops — "no added matter loop, no neutrino or conformal-scalar
loops, nothing not forced by S_IF" — because a hand-inserted matter bath generating needed
structure is precisely the **relocation** failure the program's kill-conditions exist to
catch. The record would rather have no matter sector than a laundered one.

> **STATUS: ASSUMPTION (a standing methodological fence, not a physics claim: matter
> content may not be inserted to rescue a derivation)** — (source:
> `SPECIALIST_BRIEF_rung3_spine.md`, Sharpening 1 and its restatement).

### 2.3 The trace-anomaly α leg: the one place SM-type field content touches a coefficient

Of the framework's four load-bearing legs (in-in/CTP; Mori–Zwanzig; FDT/KMS; the
trace-anomaly α leg — all borrowed, all source-verified), the α leg is the only one whose
content is a property of *matter* quantum field theory: the conformal anomaly's a and c
coefficients. The record splits it in two (the rung-9 split, banked 2026-06-27):

**The value.** a/c = 1/3 is carried as a **conditional theorem adopted as a dimensionless
axiom**: *if* the conformal mode is the IR carrier, *then* a/c = 1/3
(Komargodski–Schwimmer 2011 / Duff). It is explicitly NOT an absolute anchor and carries
**zero anchor credit** — the −1 anchor credit is suspended, not deleted.

> **STATUS: ASSUMPTION (a borrowed conditional theorem adopted as the single dimensionless
> axiom; register tier `shown` scoped strictly to the conditional; zero anchor credit)** —
> (source: `provenance/claims.json` node `rung9a_value`).

**The bridge.** c₀ = α — the claim that the anomaly *derives* the DC normalization of the
TT response kernel — is **settled-negative**: an adopted phenomenological parameter,
obstruction-backed, not forbidden. The mechanism was refined by computation (2026-08-03,
`calc/anomaly_c0_map.py`): the a-anomaly (b′) reaches the spin-0 channel *only*, the
c-anomaly (b) reaches the spin-2 channel *only*, so α = a/c is a ratio of coefficients
living in orthogonal channels — the coefficient of neither. The grade guard on that node
is explicit: a better-computed obstruction is still an obstruction, not an impossibility
proof, and the tier did not move. The node is frozen (Version I), reopenable only on a
genuinely new metric-built scalar→TT intertwiner.

> **STATUS: ASSUMPTION (STRUCTURAL-SELECTION — c₀ = α is an adopted DC normalization; the
> bridge is settled-negative, obstruction-backed, NOT forbidden; frozen)** — (sources:
> `provenance/claims.json` node `rung9b_bridge`; `GRUT_MODEL_FRAMEWORK.md` §2;
> `GRUT_ToE.md` §2.3).

This is as close as the frozen record comes to a Standard-Model interface: the anomaly
coefficients that count matter field content enter as a borrowed conditional normalization
— and the record's own computation showed the borrowing does not close.

### 2.4 Yukawa, but not flavor

The word "Yukawa" does occur in the record outside the merge-criterion exemplar — in
`provenance/prereg/RESULT_KAPPA_2026-08-08.txt` — and Phase 11's adversarial leg caught
that its first sweep missed this. The occurrences are **Yukawa-screened-potential physics**
(a screened fifth-force mass in the κ activation-scale analysis), not flavor structure.
The sector verdict survives; the evidence sentence was repaired at source.

> **STATUS: UNMAPPED (flavor) — the Yukawa occurrences are screened-potential physics,
> not Yukawa couplings** — (source: `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §H).

### 2.5 The archived strong-CP conjecture: uncertified lineage

Phase 11's Leg A found strong-CP and flavor content **in archived branches**:
`origin/v1-retired` carries `grut_solver/sectors/qcd/strong_cp.py` and a "Conjecture SCP"
with an explicit falsifier ("predicts NO axion … detection of an axion would falsify").
This is **scope-contested, not scope-free**: the repository README declares the earlier
lineage is not certified by this repository, and the mapping recorded the item as **an
owner question, not resolved**. This corpus therefore reports it as uncertified history
and gives it no status beyond that.

> **STATUS: REVERSED-adjacent history, uncertified (archived-branch content outside the
> frozen record; recorded as an open owner question)** — (source:
> `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §H).

### 2.6 The register's absence bookkeeping itself

For completeness: the register's coverage instrument (`provenance/coverage.py`) maintains
the `KNOWN_GAPS` list quoted in §1 with the standing rule "absent != covered" — the
program's own statement that naming an absence confers no coverage. This book operates
under that rule.

> **STATUS: ASSUMPTION (a governance convention of the register, applied here)** —
> (source: `provenance/coverage.py`).

## 3 · The electroweak sector as it actually appears: the vacuum cluster

The record's only sustained contact with electroweak and Higgs physics is **not a GRUT
account of either**. It is the vacuum-cluster mapping wave (2026-08-04,
`VACUUM_CLUSTER_MAP.md`; 21 register nodes at `ledger_scope: vacuum-cluster`) — the first
application of the program's tier-marking discipline to physics at large. Its scope fence
is hard: it is a **map** of how many independent underived inputs the cosmological-constant
/ hierarchy cluster contains, not a resolution of anything. GRUT was excluded as a lens
throughout (kill-condition KC5); its relation to the cluster is a single node drawn last,
marked **decorative, zero credit** (`vc_grut_relation`). The cluster runs its own tier
vocabulary (`measured` / `postulate` / `heuristic` / `open`), verified by execution to be
unable to bleed into GRUT's ledger. Statuses in this section are therefore reported in
that scoped vocabulary, with the fence stated.

What the map established that touches this book's scope:

**The independence verdict.** L (the vacuum-energy input) and H (the electroweak-hierarchy
input) are independent **under exactly one reading**: no merge reduces the underived-input
count. The strongest merge candidate — Banks-type cosmological SUSY breaking, which lands
M_S = √(ρ_obs^¼ M_Pl) ≈ 2.3–5.2 TeV inside the hierarchy window — scores **TRADE** under
the repaired criterion v2 (−1 real parameter, +1 posited relation): *not refuted*, merely
a trade the analysis declines.

> **STATUS: (vacuum-cluster scope) the post-firewall verdict as banked — independence
> under the reading that declines the trade; weaker than "proven"** — (source:
> `VACUUM_CLUSTER_MAP.md` Ruling 1).

**The spine that survived.** The one supporting argument that survived every attack is
D0(ii): in flat-space QFT, ℒ → ℒ + c is an exact symmetry — an additive constant appears
in no S-matrix element — and **gravity breaks that symmetry** by coupling c to g_μν. So L
carries a load-bearing premise (the field-independent constant gravitates) that H does not
carry at all. This is a theorem of ordinary QFT, predating every framework in the
discussion; it is background physics the map leaned on, not a GRUT result.

> **STATUS: (vacuum-cluster scope) the surviving spine of Ruling 1 — standard-QFT
> content, attacked four ways, unbroken; two of the original three proof legs (P1(i), R1)
> WITHDRAWN and recorded as such** — (source: `VACUUM_CLUSTER_MAP.md` Ruling 1).

**The Higgs enters as an input, not a dynamics.** The electroweak scale v is a cluster
node of tier `measured` (`vc_v_ew`); the hierarchy problem's load-bearing premise —
that heavy states coupling to the Higgs exist above v — is a **contested postulate**
(`vc_heavy_thresholds_exist`), whose own statement records the only neutrino-mass-adjacent
physics sentence in the working tree: no such threshold is established, because "seesaw
assumes Majorana neutrinos, Dirac neutrinos give none, GUT/PQ are inferences." Dropping
the postulate dissolves the hierarchy problem-statement (Bardeen's position).

> **STATUS: (vacuum-cluster scope) `measured` (v) and `postulate — contested` (heavy
> thresholds), per the register; NOT a GRUT account of electroweak physics** — (source:
> `provenance/claims.json` nodes `vc_v_ew`, `vc_heavy_thresholds_exist`).

**The famous number, corrected.** The wave's own sharpest-looking argument — that a hard
3-momentum cutoff gives w = +1/3, "a radiation fluid, not a cosmological constant" — was
**struck as a regulator artifact** (the arithmetic exact, the inference wrong: a covariant
regulator restores w = −1 and *raises* the magnitude). What replaces it is stronger and
smaller: the covariant magnitude carries a ~2.3-order scheme band with an undetermined
sign, stacked on a ≥5-order convention span — while the scheme-independent core stands
untouched: established thresholds alone (electron ~10^31, QCD condensates ~10^43–10^44.5,
electroweak vacuum depth 10^54.675, each × ρ_obs) need no regulator. "The problem does not
evaporate. Its famous number does."

> **STATUS: (vacuum-cluster scope) Ruling 2 as banked — "120 orders" not load-bearing;
> the struck w = +1/3 argument recorded as the wave's own caught error** — (source:
> `VACUUM_CLUSTER_MAP.md` Ruling 2).

**The count, refused.** N = 10 (the headline count of independent inputs) was **refused as
an output**: the criterion does not determine it (tight reading ~6–8, loose 12–13, >15
under the loosest). The deliverable is a **typed inventory** — 3 measured, 11 postulates
(4 contested, 7 standard), 2 heuristics, 2 open — with the ruling *the types do not
commute; there is no total*. Among the omission-repairs is `vc_universal_metric_coupling`:
universal metric coupling / the equivalence principle, presupposed by three other nodes
and booked by none — the cluster's closest thing to a "how does matter couple" statement,
and it is a *bookkeeping* statement.

> **STATUS: (vacuum-cluster scope) Ruling 3 as banked — typed inventory, integer refused
> by overseer ruling** — (source: `VACUUM_CLUSTER_MAP.md` Ruling 3;
> `provenance/claims.json` `vc_*` nodes).

**And GRUT's own position against this map** is a register node, not a hope:

> **STATUS: UNRESOLVED (open field: GRUT does not determine Λ; "an open-system framing
> that, like every other entry, must supply the measured value rather than explain it")**
> — (sources: `provenance/claims.json` nodes `lambda_undetermined`, `vc_grut_relation` —
> the latter decorative, zero credit, by construction).

## 4 · What the program's external audit says about the Standard Model — clearly not GRUT content

One further body of matter-sector text exists in the record and must be labeled with care:
`RAI_STRUCTURAL_THEORY_SEARCH.md`, the program's audit instrument turned on **physics at
large**. It records, as survey findings about standard physics (marked [VERIFIED] /
[LITERATURE] in that artifact): that literal SM+GR is false as stated (it predicts
m_ν = 0, Ω_c = 0, η_B ≈ 0 against three measured quantities, so only the framework claim
is defensible); that the electroweak transition is a **crossover, not first order**, at
the observed Higgs mass (lattice endpoint m_H ≈ 72.4 ± 1.7 GeV vs 125.20 GeV observed;
hep-ph/9809291) — so Sakharov's departure-from-equilibrium condition is absent in the
minimal theory, constraining baryogenesis mechanism-space; and that the SM's depth label
for all 13 flavor parameters is **REPRODUCTION**, never PREDICTION. These are the
program's *recorded readings of external physics*, load-bearing for its comparative
judgments, and they are the closest thing the record holds to a Standard-Model worldview.

> **STATUS: not GRUT claims — audit-recorded standard-physics findings, carried with that
> artifact's own [VERIFIED]/[LITERATURE] marks; cited here as context only** — (source:
> `RAI_STRUCTURAL_THEORY_SEARCH.md` §1).

## 5 · The absence map proper: what a constitutive account would have to supply

GRUT's architecture is explicit about what constitutes a sector account (Books I–II): a
declared system/bath decomposition for the sector; a retarded kernel and noise kernel on
declared channels; the KMS/FDT lock enforced; passivity per channel; and every input
priced as axiom, empirical input, or structural selection. Measured against that template,
here is what each topic would minimally require — and the explicit statement, in each
case, that **the record supplies none of it**. Nothing in this section is a proposal;
it is the shape of the hole.

- **Flavor** would require the Yukawa sector — three generations, mass hierarchies, CKM
  and PMNS mixing — re-expressed as constitutive response structure: some declared kernel
  whose channel decomposition *is* the generation structure, with the thirteen flavor
  parameters either derived, or honestly priced as thirteen inputs. The record contains no
  such kernel, no such channel decomposition, and no pricing. **The record supplies
  nothing here.**
- **Strong CP** would require θ̄'s smallness as a relaxation or response statement — and
  any such account would have to face the axion alternative explicitly (the uncertified
  archived conjecture shows the lineage once gestured at exactly this, with a no-axion
  falsifier; the frozen record neither adopts nor develops it). **The record supplies
  nothing here.**
- **Neutrino masses** would require the mass mechanism (Dirac vs Majorana) to enter as a
  declared input or derived structure; today the working tree's only engagement is a
  prohibition (no neutrino loops in the kernel derivation) and one hierarchy-bookkeeping
  sentence (§3). **The record supplies nothing here.**
- **Dark matter** would require either new bath content (a second internal scale — which
  the standing proviso of §2.1 currently *disallows* undischarged) or a demonstration that
  responsive-vacuum dynamics mimics cold collisionless matter at the relevant scales; the
  one line that tried (the substrate line) is retired with the superseded book. **The
  record supplies nothing here.**
- **Baryogenesis** would require out-of-equilibrium dynamics with C/CP violation inside a
  framework whose equilibrium physics is locked by KMS/FDT — the record has not even posed
  the question of what its non-equilibrium sector permits. **The record supplies nothing
  here.**
- **Higgs/electroweak dynamics** would require the electroweak vacuum itself treated as a
  responsive medium — symmetry breaking, the crossover, vacuum stability — none of which
  appears; v enters only as a measured cluster input. **The record supplies nothing
  here.**
- **QCD** would require confinement-scale response physics; the record holds only the
  condensates' contribution to vacuum-energy bookkeeping. **The record supplies nothing
  here.**
- **Matter–vacuum coupling** would require, at minimum, the universal-metric-coupling
  presupposition (§3) promoted from an omission-repair bookkeeping node to a derived or
  priced statement about *how* matter sources the responsive vacuum; within GRUT proper,
  matter couples only as the §2.1 bath selection. **The record supplies nothing beyond
  those two bookkeeping entries.**

> **STATUS: UNMAPPED (each item above; the requirements lists are structural readings of
> the framework's own architecture — `GRUT_MODEL_FRAMEWORK.md` §§2–3 — not proposals, and
> deliberately carry no candidate mechanisms)** — (sources as marked in §1).

Two closing discipline notes. First, none of these holes may be filled by fiat: the
program's stopping rule permits a new foundational move only on an independently motivated
principle naming a specific phenomenon the framework cannot represent — never "we need X
because not-X failed" (`GRUT_PROGRAM_FREEZE.md` §1) — and the standing fences (§2.2;
the signature audit's laundering checks) exist precisely to keep inserted matter content
out. Second, the absence has a known cost the record has already priced: the PREDICTED set
is empty —

> **STATUS: EMPTY (nothing has earned entry; Book IX governs entry)** — the PREDICTED set,
> canonical table item 21 (source: `books/CORPUS_CHARTER.md`).

— and Phase 10's ruling makes mapping flavor and strong-CP the *prerequisite* for any
fresh discriminator pool. The matter sector is thus not merely where GRUT is silent; it is
where the program's own governance says the next honest work would have to begin, if the
owner ever reopens it. The two items Phase 11 actually added to the map
(`bh_ringdown_qnm` and `gamma_T_siren_amplitude`, both MAPPED-UNRESOLVED) are
gravitational-wave observables, not matter-sector ones — even the record's frontier
candidates live outside this book.

> **STATUS: UNRESOLVED (two MAPPED-UNRESOLVED map additions exist; neither is a
> matter-sector item; no target selected, nothing computed)** — (source:
> `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` §M).

---

## Sources drawn from

- `books/CORPUS_CHARTER.md` (canonical status table; vocabulary; formatting)
- `GRUT_MODEL_FRAMEWORK.md` (primitives table — bath content, c₀ = α; architecture §§2–3)
- `GRUT_PROGRAM_FREEZE.md` (stopping rule; ledger; PREDICTED-empty)
- `PHYSICS_LEDGER/FOREST_PHASE11_MAPPING.md` (the sector-by-sector mapping; §§A, H, I, M)
- `PHYSICS_LEDGER/FOREST_PHASE10_RESULT.md` (flavor/strong-CP prerequisite ruling; the
  massive-neutrino baseline remark)
- `provenance/claims.json` (nodes `rung9a_value`, `rung9b_bridge`, `lambda_undetermined`,
  `vc_v_ew`, `vc_heavy_thresholds_exist`, `vc_grut_relation`, `vc_averaging_commutes`,
  `vc_universal_metric_coupling`, and the vacuum-cluster set; 74 nodes, read-only)
- `provenance/coverage.py` (KNOWN_GAPS; "absent != covered")
- `provenance/merge_criterion.py` (the θ̄ / y_e counting exemplar)
- `VACUUM_CLUSTER_MAP.md` (Rulings 1–3; the typed inventory; the struck w = +1/3 argument)
- `EMERGENCE_CHAIN.md` §11 (the SILENT matter link)
- `SPECIALIST_BRIEF_rung3_spine.md` (the matter-loop prohibition)
- `SIGNATURE_AUDIT.md` (verdict classes; laundering checks; context for §5)
- `RAI_STRUCTURAL_THEORY_SEARCH.md` §1 (the external structural audit's SM findings;
  external citation hep-ph/9809291 as that artifact carries it)
- `GRUT_ToE.md` §§1.3, 2.3, 2.6, 4.2 (the four legs; the α-leg split; differentiators;
  the empty prediction column)
- `GRUT_II_What_Survived.md` (zero novel positive predictions)
- `docs/WHERE_IT_STOPS.md` and `handover/SUPERSEDING_NOTE.md` (the retired dark-matter
  substrate line)
- `provenance/prereg/RESULT_KAPPA_2026-08-08.txt` (the Yukawa-screened-potential
  occurrences)
- `books/BOOK_I_FOUNDATIONS.md` (cross-book consistency on canonical item 22)

## Gaps in this book

1. **The book's subject is itself a gap.** Flavor, strong CP, neutrino masses, dark
   matter, and baryogenesis have no GRUT account (canonical item 22); this book maps that
   absence and adds no account.
2. **The archived-branch strong-CP conjecture is unexamined here** beyond its Phase-11
   citation: it lives in an uncertified lineage (`origin/v1-retired`), its adjudication
   is an open owner question, and this book neither reads nor grades its contents.
3. **The §5 requirements lists are this book's own structural readings** of the
   framework's architecture — reasonable-minimum statements of what an account would need,
   not register content; a future audit may sharpen or replace them.
4. **No search of uncommitted session records** was performed for matter-sector content;
   this book covers the committed v4 working tree, inheriting Phase 11's declared scope
   (and Phase 11's own sweep-narrowness corrections — `.txt`/`.log`/archived-register
   blindness — are only partially compensated by its Leg-A repairs).
5. **The vacuum-cluster treatment is summary, not reproduction**: the five undecided
   pairs, the merge-criterion arc (v1→v2→v3→reframe), and the per-node riders are carried
   in `VACUUM_CLUSTER_MAP.md` and the `vc_*` nodes, not restated in full here.
6. **The record is silent — and so is this book — on** any GRUT statement about gauge
   coupling running, proton stability, electric-charge quantization, the number of
   generations, or any collider observable. No source in the repo poses these questions.
