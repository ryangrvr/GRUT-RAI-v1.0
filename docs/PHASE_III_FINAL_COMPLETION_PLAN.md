# Phase III Final Completion Plan

**DATE**: 2026-03-12
**PURPOSE**: Dependency-aware execution plan for the final Phase III pre-Zenodo pass
**CANON VERSION**: v0.3.6 (input state)

---

## A. Remaining Item List (1–9)

| # | Item | Current State | Classification |
|---|------|--------------|----------------|
| 1 | Explicit effective T^Φ_μν | SCHEMATIC — placeholder in field equations | MUST RESOLVE SUBSTANTIALLY |
| 2 | Action / Lagrangian status | UNCLASSIFIED — no assessment exists | MUST CLASSIFY HONESTLY |
| 3 | Junction conditions with memory | NOT ATTEMPTED | MUST RESOLVE SUBSTANTIALLY |
| 4 | Tidal Love numbers | NOT ATTEMPTED | MUST RESOLVE SUBSTANTIALLY |
| 5 | Kerr / spin extension | NOT ATTEMPTED | MUST CLASSIFY HONESTLY |
| 6 | Nonlinear mode coupling | NOT ATTEMPTED | MUST CLASSIFY HONESTLY |
| 7 | Transition-width in covariant closure | WP2D validated sharp limit; not folded into covariant | MUST RESOLVE SUBSTANTIALLY |
| 8 | Tensorial memory-sector generalisation | OPEN — scalar vs tensor unclassified | MUST CLASSIFY HONESTLY |
| 9 | Observability / detector relevance | NO ASSESSMENT — raw amplitudes only | MUST CLASSIFY HONESTLY |

**Classification key**:
- MUST RESOLVE SUBSTANTIALLY: requires new derivation, module, and tests
- MUST CLASSIFY HONESTLY: requires rigorous assessment and bounds, may not be fully solvable
- MAY REMAIN OPEN IF SHARPLY LOCALISED: acceptable to leave as flagged research target

---

## B. Dependency Graph

```
                    ┌─────────────┐
                    │ 1. T^Φ_μν   │
                    │  (explicit   │
                    │   effective) │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
     ┌────────────┐ ┌───────────┐ ┌──────────┐
     │ 2. Action  │ │ 3. Junct- │ │ 8. Tensor│
     │  / Lagrang.│ │  ion cond.│ │  vs scalar│
     │  status    │ │  + memory │ │  comparis.│
     └────────────┘ └─────┬─────┘ └──────────┘
                          │
                    ┌─────┼─────┐
                    │     │     │
                    ▼     ▼     ▼
              ┌───────┐ ┌───┐ ┌──────────┐
              │4. Love│ │ 7 │ │5. Kerr   │
              │numbers│ │   │ │(bounded) │
              └───┬───┘ └───┘ └────┬─────┘
                  │                │
                  ▼                ▼
            ┌──────────┐    ┌──────────┐
            │6. Nonlin.│    │9. Detect.│
            │  coupling│    │  summary │
            └────┬─────┘    └────┬─────┘
                 │               │
                 └───────┬───────┘
                         ▼
                  ┌─────────────┐
                  │ PACKAGE D   │
                  │ Final doc   │
                  └─────────────┘
```

---

## C. Correct Execution Order

**Phase 1 — PACKAGE A** (Memory Tensor Closure): Items 1, 2, 8
- Derives T^Φ_μν constitutively from sector equations
- Classifies action / Lagrangian status
- Compares scalar vs tensor memory
- **Blocks**: everything downstream

**Phase 2 — PACKAGE B** (Boundary / Matching Closure): Items 3, 7
- Derives junction conditions with memory field at R_eq
- Folds transition-width into covariant framework
- **Requires**: T^Φ_μν from Package A
- **Blocks**: Love numbers (need boundary conditions)

**Phase 3 — PACKAGE C** (Final Observable Closure): Items 4, 5, 6, 9
- Tidal Love numbers (requires junction conditions from B)
- Kerr / spin extension (bounded first pass)
- Nonlinear mode coupling (bounded first pass)
- Observability / detector relevance summary
- **Requires**: Packages A and B

**Phase 4 — PACKAGE D** (Closure Document): Synthesis
- Final Phase III upload state document
- **Requires**: Packages A, B, C complete

---

## D. What is Truly Blocking What

| Blocked Item | Blocked By | Reason |
|-------------|-----------|--------|
| Action status (2) | T^Φ_μν (1) | Cannot assess whether action exists without knowing what T^Φ is |
| Junction conditions (3) | T^Φ_μν (1) | Must know what memory stress-energy is continuous/discontinuous at boundary |
| Tensor comparison (8) | T^Φ_μν (1) | Must know scalar T^Φ explicitly to compare against tensorial alternative |
| Love numbers (4) | Junction conditions (3) | TLN depends on boundary condition at R_eq |
| Transition in covariant (7) | Junction conditions (3) | Folding transition layer requires matching structure |
| Detectability (9) | Love numbers (4), Kerr (5) | Need numerical estimates to assess detector relevance |
| Final document (D) | All packages | Synthesis requires all results |

---

## E. Partially vs Fully Solved Before Upload

| Item | Target Level | Rationale |
|------|-------------|-----------|
| 1. T^Φ_μν | SUBSTANTIALLY — constitutive derivation, explicit components | Core remaining closure |
| 2. Action | CLASSIFICATION — honest status, not full action derivation | May not be achievable |
| 3. Junction | SUBSTANTIALLY — Israel conditions adapted for GRUT, matching checks | Connects interior to exterior |
| 4. Love numbers | SUBSTANTIALLY — first-pass estimate with reflecting boundary | Potential non-null observable |
| 5. Kerr | BOUNDED FIRST PASS — parametric estimates, not full solution | Full Kerr is multi-year program |
| 6. Nonlinear | BOUNDED FIRST PASS — amplitude scaling, Q correction estimate | Full nonlinear is research program |
| 7. Transition | SUBSTANTIALLY — connect WP2D to covariant metric | Well-defined extension |
| 8. Tensor vs scalar | CLASSIFICATION — structural comparison, not tensorial derivation | Tensorial theory is future work |
| 9. Detectability | CLASSIFICATION — rough SNR estimates, detector landscape | Not a pipeline |

---

## F. Phase III Upload Readiness Criteria

The Phase III Zenodo upload is ready when:

1. All 9 items are either substantially resolved OR sharply localised with explicit bounds
2. T^Φ_μν has an explicit effective form (not just "schematic")
3. Junction conditions exist and connect interior/exterior
4. At least one quantitative Love number estimate exists
5. Kerr and nonlinear coupling have honest first-pass bounds
6. Detectability summary exists with rough SNR categories
7. All nonclaims are preserved and updated
8. Full test suite is green
9. Final closure document separates LOCKED / CONSTRAINED / OPEN / POST-PHASE-III
