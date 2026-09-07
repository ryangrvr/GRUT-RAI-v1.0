# RESULTS — Q2 stochastic SY run

> Machine labels only. NO scientific adjudication is performed here; see
> `program/gates/Q2_STOCHASTIC_EXECUTION_PREREG.md` §18 for the frozen decision
> tree. This instrument evolves the SCALAR SY channel and is NOT O2.

- instrument sha256: `3cda78997eaa5314f043594e6ce554e2734812f392fdd8882a326a3c1b6ad2b9`
- config sha256: `4aac62a44ac0ad65afe574d6e05eee5c5f3484e17e641aa680d08e5ae91ff4dc`
- python 3.15.0a2 · RNG python stdlib random.Random (Mersenne Twister MT19937), .gauss(0,1)
- seeds: [20260907, 20260908, 20260909, 20260910, 20260911]
- wall seconds: 1250.3

## Preregistered comparison targets (emitted before measurement)

- target A (record composition m_eff^2/3H): 0.033333 H
- target B (SY Fokker-Planck eigenvalue): 0.008850 H

## Primary estimator O1a (stationary connected autocorrelation, LAG coordinate)

| seed | rate | r2 | n_lags |
|---|---|---|---|
| 20260907 | 0.009916783754546143 | 0.9976787498673437 | 641 |
| 20260908 | 0.009642116142770338 | 0.9965286498614788 | 641 |
| 20260909 | 0.009236259217764626 | 0.9977129267829217 | 641 |
| 20260910 | 0.008866147551328373 | 0.9996139961509571 | 641 |
| 20260911 | 0.008418889115869198 | 0.9990074393848656 | 641 |

## Cross-check O1b (ensemble-mean decay, ABSOLUTE TIME, transient phase)

| seed | window | rate | r2 |
|---|---|---|---|
| 20260907 | [5.0, 40.0] | 0.006963967332276746 | 0.9888759028854369 |
| 20260907 | [5.0, 65.0] | 0.007737972434700484 | 0.9951756625492888 |
| 20260907 | [30.0, 70.0] | 0.008365152317745667 | 0.9969284304612761 |
| 20260908 | [5.0, 40.0] | 0.0066057109507208335 | 0.9783093780023819 |
| 20260908 | [5.0, 65.0] | 0.007587108433926531 | 0.9913332869900994 |
| 20260908 | [30.0, 70.0] | 0.008300962993777933 | 0.9974194061500304 |
| 20260909 | [5.0, 40.0] | 0.006643056657129667 | 0.9958367215986377 |
| 20260909 | [5.0, 65.0] | 0.0066821958981004076 | 0.9966519444835633 |
| 20260909 | [30.0, 70.0] | 0.007406743276726996 | 0.9869436523308116 |
| 20260910 | [5.0, 40.0] | 0.006554475004332125 | 0.991576359275603 |
| 20260910 | [5.0, 65.0] | 0.007846596854584829 | 0.9886752361805701 |
| 20260910 | [30.0, 70.0] | 0.008897643098981053 | 0.995604203710824 |
| 20260911 | [5.0, 40.0] | 0.0065387579390242916 | 0.9933128151253916 |
| 20260911 | [5.0, 65.0] | 0.007287436934059169 | 0.9954682562610412 |
| 20260911 | [30.0, 70.0] | 0.007785841344946142 | 0.9955331593454472 |

## Aggregate

```json
{
 "primary_rate": {
  "mean": 0.009216039156455736,
  "sd": 0.0005349515423746109,
  "n_seeds": 5,
  "seed_spread_relative": 0.0580457106673514
 },
 "evaluation": {
  "measured_rate": 0.009216039156455736,
  "target_A": {
   "target": 0.03333333333333333,
   "relative_deviation": 0.7235188253063279,
   "label": "NOT_OBSERVED"
  },
  "target_B": {
   "target": 0.00885,
   "relative_deviation": 0.041360356661665064,
   "label": "OBSERVED"
  },
  "seed_stability": {
   "spread": 0.0580457106673514,
   "label": "CONVERGED"
  },
  "discrimination": "OBSERVED",
  "note": "Labels are machine states, not scientific verdicts. Adjudication against the frozen decision tree (prereg section 18) is the audit layer's and the owner's. 'OBSERVED' for a target means only: consistent within tol_rate."
 }
}
```
