# MANIFEST — GRUT-RAI release `zenodo-v1.0`

**Version:** zenodo-v1.0 · **Date:** 2026-09-07 · **Author:** D. Ryan Grover
**Source of record:** git repository `github.com/ryangrvr/GRUT-RAI`, branch `v4`, tag `zenodo-v1.0`.

## Authority rules

1. For every document present both in the repository and in this package, the
   **repository copy at the tagged commit is authoritative**; package copies are the
   frozen release snapshot (byte-identical at release time — checksums below).
2. Within `02_BOOKS/`, the **`.md` file is the authoritative source of each book**; the
   PDF is generated from it (python-markdown 3.10.3 → styled HTML → headless Chrome
   150 print-to-pdf) and carries no independent edits.
3. `01_PROGRAM/claims.json` is the program's 74-node claims register — **read-only to
   the entire corpus**; no book, audit, or release step modified it.
4. Materials of the RRT arm live on repository branch `rrt0-phase2` and are cited, not
   copied, into this release.
5. This release is a publishing pass over the frozen record: the corpus-to-release diff
   is pure insertion (front matter + tables of contents), verifiable in the repository
   history.

## Files

| file | bytes | sha256 |
|---|---|---|
| `README.md` | 4388 | `d065dd43e412d046ee7f7950a6e39a752c16cc967ffd90079fe95735e258b4c7` |
| `01_PROGRAM/GRUT_MODEL_FRAMEWORK.md` | 13609 | `23df6607e730ec2f42299e1fc8fb93ddb51f6f93f35334535de10ddb67a1b9e3` |
| `01_PROGRAM/GRUT_NEXT_STEPS.md` | 3145 | `58a1047fb0e7b38d4543f2e9ba8a513f1cb4c2b654b5dc2b8850a87a2d649372` |
| `01_PROGRAM/GRUT_PREDICTION_GATE_GAMMA_T.md` | 14908 | `2c2df5ae01738b5fd76bdd32db074aa15a3a88ca9f33ab8c326e8aa77efcdb96` |
| `01_PROGRAM/GRUT_PROGRAM_FREEZE.md` | 11584 | `2dfd9c63c3779404ad12210a7ad6739af212dba031e07f049ee89effdf814718` |
| `01_PROGRAM/RESULTS_gw_tensor_friction.md` | 7117 | `a0f8a321cba12325e794be99388da922bf015e0922f0777bb08682df6b3ecca2` |
| `01_PROGRAM/ROOT1_KERNEL_ORIGIN.md` | 16193 | `0106c8ba6aa40b0cd69c10abd8e84b9cc2a96f91e2a53affd2d58191ff5bc107` |
| `01_PROGRAM/SIGNATURE_AUDIT.md` | 13656 | `798094c6294d70ea4c58d618891c96c67808b8cf13bbd6cc39962f8077d2334e` |
| `01_PROGRAM/SPEC_gw_tensor_friction.md` | 6877 | `c7bd2ef03168c185eb90fea2ace3388e39eb3a7b7dad0ba8e3d0ab6c04bf5b6c` |
| `01_PROGRAM/claims.json` | 336616 | `beaeb84e8a6f84681e6625c1ee5f3b42d5c3f0a978a93256313e77ba65572402` |
| `01_PROGRAM/gw_tensor_friction.py` | 15328 | `bea7805008ce429318025ed74b0ecdf73f41a4cd52692539e6191da271c3b8eb` |
| `02_BOOKS/BOOK_III_QUANTUM_REALITY.md` | 36283 | `6fa125a6a70633186b58792a7973f39539ddfa6d675d4adb84bc990132a3458d` |
| `02_BOOKS/BOOK_III_QUANTUM_REALITY.pdf` | 368053 | `b2a07a0c2420f2b58bd0528b04004226b9c578afa51c5c3695f26e8b01347d1f` |
| `02_BOOKS/BOOK_II_CONSTITUTIVE_FRAMEWORK.md` | 41847 | `b5348e31b5191045aedf1205597dfdab868ccb23056a8b1caf51f85b6ef7b59d` |
| `02_BOOKS/BOOK_II_CONSTITUTIVE_FRAMEWORK.pdf` | 381200 | `ce6b96ffd3fcf971611f061dac8c2ee222c5d3fac8785ac89d6cfc7fe2d55052` |
| `02_BOOKS/BOOK_IV_GRAVITY_SPACETIME_RESPONSE.md` | 39929 | `77d4052ff79577ac35d75ee16505fdc3facd7eb306aa8d872fb70e9e5f3f0dc0` |
| `02_BOOKS/BOOK_IV_GRAVITY_SPACETIME_RESPONSE.pdf` | 386090 | `931d48ad08fa9f9a18af8c5ee47d67d504129f460d22afa3872a475640460581` |
| `02_BOOKS/BOOK_IX_TESTS_PREDICTIONS.md` | 47692 | `09cb43dca5fd3b214200e0a4ca735e032d014913211ee04272c47277ecabe3e3` |
| `02_BOOKS/BOOK_IX_TESTS_PREDICTIONS.pdf` | 449947 | `31f40153c0a0cb514936e84884b1f6369bb61b7ec657f452962ed03d2807422f` |
| `02_BOOKS/BOOK_I_FOUNDATIONS.md` | 37135 | `c8d26b8f2d5ce5093cda27ed5ce1151ed4dd7d3301f3a4882e7792202e5c18b0` |
| `02_BOOKS/BOOK_I_FOUNDATIONS.pdf` | 403868 | `d08c5146bcf48e8a004de589d3f20c7796be30acbef86093ce0e95fcfd040aa2` |
| `02_BOOKS/BOOK_VIII_EMERGENCE_OBSERVATION_RELATIONAL.md` | 43614 | `ea60519c0be4161ac6e2192e03f56a29fa604be90099d4070bb0e78a1830ea63` |
| `02_BOOKS/BOOK_VIII_EMERGENCE_OBSERVATION_RELATIONAL.pdf` | 371006 | `d0a7b95b0408019cd965d74c291e1a5b9ca12fc1f0e64a513dfcec532e171fbd` |
| `02_BOOKS/BOOK_VII_MATTER_SM_INTERFACE.md` | 29752 | `dcd46113212faf65b18ea13bd6392824f7658fb5b2450aa0c18f4bf7450ac348` |
| `02_BOOKS/BOOK_VII_MATTER_SM_INTERFACE.pdf` | 320088 | `e558845784260b75f7dbd8c7ddb4b0470b0d79851b53ea7231d4c6056270d445` |
| `02_BOOKS/BOOK_VI_COSMOLOGY.md` | 38829 | `d7f4ee9c6c57b1888972d9d419fb80dd6ae0bae4223b124f4429fb16d7656c54` |
| `02_BOOKS/BOOK_VI_COSMOLOGY.pdf` | 450149 | `01656e6c324575e150adbf1f109733f175aa5134fc39cc575bea62025fc812c5` |
| `02_BOOKS/BOOK_V_MEMORY_THERMODYNAMICS_TIME.md` | 44044 | `e67297119c80d0d06dde88f927aa47b5636d41ce916c7980027659fc4020f021` |
| `02_BOOKS/BOOK_V_MEMORY_THERMODYNAMICS_TIME.pdf` | 382491 | `257be3d26867f851c7eb31fa7441108ff2f0ca49a61a6867e0edcb01d6f1a837` |
| `02_BOOKS/BOOK_X_RESEARCH_PROGRAM.md` | 46384 | `d7be760938fd636782e5ad7b9a40f8d8e96617f96f77c8f52b951a3eac94129d` |
| `02_BOOKS/BOOK_X_RESEARCH_PROGRAM.pdf` | 425106 | `0da6365e12e38bbbf7622a5965a05eed14dc46f25dd071fd7762d417dc7b9291` |
| `02_BOOKS/CORPUS_CHARTER.md` | 10646 | `292427fc89122b3213e53b2bd7b7ae6f723d8b193136630612d7ee95e8d4e515` |
| `02_BOOKS/CORPUS_CHARTER.pdf` | 217578 | `89553ff33f7971f104b952d54356ca84e85f9fbd9f3e45d084787ba4f066b2b4` |
| `02_BOOKS/READERS_MAP.md` | 6719 | `d5847476c4e72d5e7cbdd8bf51e43b8e1db0192646df262da89dc0fe89660ed7` |
| `02_BOOKS/READERS_MAP.pdf` | 147389 | `d999ff36bb783953798b2a6844ae1973448cf651117f704edc1c9868bce53a77` |
| `03_RAI/RAI_DIALECTIC_CHAMBER.md` | 12326 | `e49b46bae7ec86bccccb076adebe00e602269342587a55902657b36acbf61130` |
| `03_RAI/RAI_FINAL_BOSS.md` | 11194 | `90a115228b73999faf60e95b255d741d25303a77df5699cbbda86519d4fa7d5b` |
| `03_RAI/RAI_GORILLA_T1.md` | 15634 | `4ffec611ff0792c9522beb837574af8cb67257671287bf4cd98d2acc8431683e` |
| `03_RAI/RAI_GRUT_RESURRECTION.md` | 17370 | `c82fa7e7ad5ebebb6746a0ce95a25d6d16e036bc28fe68490411ada9fc4a907a` |
| `03_RAI/RAI_STRUCTURAL_THEORY_SEARCH.md` | 29165 | `74f019487e07f099734c4f147c0196089cc3e7d50fcb509cd404575dcb270ab0` |
| `03_RAI/rai_dialectic_chamber.py` | 6663 | `c1efc678a246968e238d189c7549b9a08f955a11811d84f04dbac3eb05122ddc` |
| `03_RAI/rai_final_boss.py` | 6309 | `7dd29233fb1a872eebffb02474c7a9407fffe6bc4eadf17f1becc372c9a9dbc2` |
| `03_RAI/rai_gorilla_t1.py` | 9726 | `e831f5ccee293c576c8e985216503333aee72fa44ce713b3f20c196a831adc95` |
| `03_RAI/rai_grut_resurrection.py` | 8096 | `9f7051317b1158d90904cc77af6b4b02bd70e9c92bd4157c3960ed92e89c8bf5` |
| `03_RAI/rai_structural_theory_search.py` | 7582 | `060f6639fe9c991186fd01e0e3067c35deda351f988d98ba6901c21b6ba75760` |

**45 files.** Register check: `01_PROGRAM/claims.json` sha256 = 
`beaeb84e8a6f84681e6625c1ee5f3b42d5c3f0a978a93256313e77ba65572402`.
