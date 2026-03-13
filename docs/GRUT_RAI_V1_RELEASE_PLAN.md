# GRUT-RAI v1.0 Release Plan

## Release Identity

**Name**: GRUT-RAI v1.0 — Canonical Build (Phases I–III Complete)

**Purpose**: Synchronize the GRUT-RAI codebase to the completed Phase I–III
canon.  This is the first release where every AI-facing reference, default
parameter, classification string, and status label is aligned to the final
Phase III state.  Superseded proxy results are explicitly marked.  The
three-tier status ladder (LOCKED / CONSTRAINED / OPEN) is applied
consistently throughout.

**What v1.0 is NOT**:
- Not a final first-principles closure of all GRUT
- Not the final ontology of the memory sector
- Not the end of theory development

---

## Scope

### In scope
1. Version identity strings (engine_version, init docstrings, FastAPI title)
2. AI system prompt — Phase III context, status ladder, leading results
3. Canon metadata (phase, status label)
4. Classification strings (`reactive_candidate` → `reactive` where Q > 10)
5. Default Q fallback values (515.6 → PDE-informed value)
6. Superseded-result banners on pre-PDE documents
7. Test updates for v1.0 vocabulary
8. GRUTipedia edition bump with Phase III summary
9. Release notes

### Out of scope
- Refactoring unrelated to canon alignment
- New physics modules
- Canon schema version bump (remains v0.3 — content changes only)
- Deleting historical documents (mark superseded, do not delete)

---

## Dependency Order

```
1.  Version identity strings           (no dependencies)
2.  Classification string cleanup      (no dependencies)
3.  Default parameter updates           (no dependencies)
4.  System prompt update                (depends on 1)
5.  Canon metadata update               (depends on 1)
6.  Superseded-result banners on docs   (no dependencies)
7.  Benchmark script fix                (depends on 2)
8.  Test updates                        (depends on 2, 3)
9.  GRUTipedia / API title              (depends on 1, 4)
10. Release notes                       (depends on all above)
```

---

## What Must Be Updated

| File | Change | Priority |
|------|--------|----------|
| `core/constants.py` | engine_version → `grut-rai-v1.0` | CRITICAL |
| `grut/__init__.py` | Docstring → v1.0 identity | CRITICAL |
| `grut/engine.py` | Default engine_version → `GRUT-RAI-v1.0` | CRITICAL |
| `ai/system_prompt.py` | Fallback version, canon line, Phase III context | CRITICAL |
| `api/main.py` | FastAPI title, hardcoded engine_version | CRITICAL |
| `grut/ringdown.py` | Q fallback 515.6 → 7.5, comment on line 126 | HIGH |
| `grut/interior_waves.py` | `reactive_candidate` → `reactive` (Q>10 branch), default Q | HIGH |
| `grut/interior_pde.py` | `reactive_candidate` → `reactive` (Q>10 branch) | HIGH |
| `grut/interior_covariant.py` | `reactive_candidate` → `reactive` (Q>10 branch) | HIGH |
| `canon/grut_canon_v0.3.json` | meta.phase → "3", meta.status → "v1.0", add v1.0 note | HIGH |
| `tests/test_collapse.py` | Rename / update stale classification tests | HIGH |
| `benchmark_phase3c_wp2d_transition.py` | Update expected classification | MEDIUM |
| `docs/PHASE_III_C_WP2C_INTERIOR_WAVES.md` | Add SUPERSEDED banner | MEDIUM |
| `docs/PHASE_III_C_WP2D_TRANSITION_WIDTH.md` | Add SUPERSEDED banner | MEDIUM |
| `README.md` | Title → v1.0 | MEDIUM |

## What Must Be Marked Superseded (NOT deleted)

- `reactive_candidate` proxy result (Q~515) → SUPERSEDED by PDE closure (Q~6-7.5, mixed_viscoelastic)
- ~3.7% echo proxy amplitude → SUPERSEDED by PDE ~1.1% and covariant ~1.1%
- Old L_stiff × V_tol endpoint → already correctly SUPERSEDED in current code

---

## Acceptance Criteria for v1.0

1. All version identity strings say `GRUT-RAI-v1.0` or equivalent
2. No code path returns `reactive_candidate` when Q > 10 — returns `reactive`
3. No default parameter uses Q = 515.6 — uses PDE-informed value
4. System prompt references Phase III final state
5. Canon metadata says phase "3", status "v1.0"
6. All pre-PDE documents have SUPERSEDED banners
7. Full test suite passes: 0 failures
8. Release notes created and accurate
9. No overclaiming introduced
