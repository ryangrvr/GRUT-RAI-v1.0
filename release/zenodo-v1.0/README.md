# GRUT-RAI — Frozen Research Record, Books Working Edition, and RAI Audit Infrastructure

**Release `zenodo-v1.0` · 2026-09-07 · D. Ryan Grover**
**Source repository:** `github.com/ryangrvr/GRUT-RAI`, branch `v4` (the git repository at the
tagged commit is the full authoritative record; this package is its load-bearing subset).

This is the first public release of the GRUT research program in its present, **frozen**
state — one coherent program, presented honestly. It is a *working edition*: a research
record and a readable corpus, **not** a completed-theory claim. The program's PREDICTED
set is currently empty, and the corpus says so on its face.

## The two objects, kept distinct throughout

- **GRUT** — the theory/framework: a constitutive-relational proposal treating the
  gravitational vacuum as a responsive medium, formulated through retarded response and
  noise kernels under causality, KMS/FDT, and passivity constraints, with every primitive
  declared and priced.
- **RAI** — the auditing/research infrastructure: the adversarial multi-agent instruments,
  pre-registration discipline, and de-pinned gate standard that *test* GRUT's claims —
  including the audits that destroyed several of the program's own founding claims.

## The story this release tells, in reading order

1. **What GRUT currently is** → `02_BOOKS/BOOK_I_FOUNDATIONS` (front door) and
   `01_PROGRAM/GRUT_MODEL_FRAMEWORK.md` (the authoritative model presentation).
2. **How it is formulated** → `02_BOOKS/BOOK_II_CONSTITUTIVE_FRAMEWORK` (mathematics),
   Books III–VIII (sector by sector).
3. **What has been derived / recovered / hypothesized** → the inline STATUS labels
   throughout the books, governed by `02_BOOKS/CORPUS_CHARTER` and its 24-entry canonical
   status table.
4. **What has failed or remains unresolved** → Book I §3 (up front, by design), Book X
   (the failure history as scientific content), and the reversals carried on the face of
   every affected claim.
5. **How RAI tests those claims** → `03_RAI/` (the five instrument records with their
   executable gates) and `01_PROGRAM/GRUT_PREDICTION_GATE_GAMMA_T.md` +
   `RESULTS_gw_tensor_friction.md` (the prediction-gate methodology demonstrated end to
   end, terminating in a computed refusal).

## The three layers

| layer | contents | role |
|---|---|---|
| `01_PROGRAM/` | model framework, program freeze + stopping rule, the Γ_T prediction gate and closure computation, the signature audit, the kernel-origin audit (ROOT-1), the 74-node claims register | the frozen technical baseline |
| `02_BOOKS/` | Books I–X + corpus charter + reader's map, each as `.md` (authoritative source) and generated PDF | the readable corpus — the primary intellectual presentation |
| `03_RAI/` | the five adversarial instrument records (Structural Theory Search, Resurrection, Gorilla-T1, Dialectic Chamber, Final Boss) with their executable verification scripts | the audit infrastructure |

New readers should start with `02_BOOKS/READERS_MAP` (orientation + glossary), then Book I.

## Working-edition statement

Every book carries this on its face: the corpus is a structured first draft built from the
frozen record under a standing directive — *no invented derivations, no
hypothesis-to-prediction promotion, no reopened gates, no new foundational generations* —
with every substantive claim labeled by epistemic status inline. This release is a
**publishing pass**: formatting, navigation, and metadata were improved; **no scientific
substance was changed in preparation** (the release commit's diff over the corpus is
pure insertion — front matter and tables of contents only).

Drafting provenance, disclosed per the program's own standards: the books were drafted by
the RAI builder agent (Claude, Anthropic) from the frozen record under owner direction,
cross-audited by an 11-agent adversarial workflow plus mechanical scans, and repaired
before release (one blocking status-promotion defect among the findings — caught and
fixed, in keeping with the program's evidentiary discipline).

## Integrity

`MANIFEST.md` lists every file in this release with its SHA-256 checksum, declares which
copy is authoritative, and records the register hash
(`claims.json`, 74 nodes, sha256 prefix `beaeb84e8a6f8468` — read-only to the entire
corpus and unchanged throughout its production).
