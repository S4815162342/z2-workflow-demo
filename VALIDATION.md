# Validation record

This file records the **maintainer's own rerun**. It is not an independent reproduction and not a scientific review. Independent reruns should be submitted through the repository's **Reproduction report** issue form, and scientific review is tracked in `HUMAN_REVIEW.md`.

## Tested environment

| Item | Value |
| --- | --- |
| Date (UTC) | 2026-11-09 19:39 |
| Code version | identified by the SHA-256 hashes of `checker.py` and `fixtures.json` below |
| Operating system | Ubuntu 20.04.6 LTS, Linux 5.15.0-139-generic, x86_64 |
| Python | 3.8.10 |
| Extra packages | none (the checker uses only the standard library) |

## Commands

Run from the repository root:

```bash
python3 checker.py
python3 -m unittest -v
python3 verify_proposal.py
```

## Results

- `python3 -m unittest -v`: 16 tests ran, all OK.
- `python3 checker.py` printed the expected summary:

  | Measure | Value |
  | --- | ---: |
  | Fixtures evaluated | 6 |
  | Execution errors | 0 |
  | Pass within the implemented checks | 2 |
  | Fail within the implemented checks | 4 |
  | Overall unresolved | 2 |
  | Overall fail | 4 |
  | Verified duals | 0 |

- `python3 verify_proposal.py`: `logged_model_proposal` has `execution_status: OK`, `scoped_status: PASS`, `overall_status: UNRESOLVED`.
- The inputs were:

  | File | SHA-256 |
  | --- | --- |
  | `checker.py` | `17755de6af037e4b0aa1db1b04ab6d5f27b4d2f6e52cfd93c82042f15fd6a6a7` |
  | `fixtures.json` | `524931f670aca56c1fc4b0b3d769ee5c5472d9d93289dd9d827da82e2cbb93cc` |

- The regenerated output files were byte-identical to the archived ones:

  | File | SHA-256 |
  | --- | --- |
  | `results.json` | `19bb2c53fc11342f26a029f61d287a69d58e6f4f25355ac88ee76052ec93ce7e` |
  | `logs/proposal_checks.json` | `ec8aaa30fd29ea0fd271bbe59a7f2152205428f457be921344fef91bd3c9cf13` |

## Report build

`bash compile_report.sh` rebuilt `report/Z2_workflow_demo_report.pdf` (6 pages) with XeLaTeX and no errors.

## Not covered

This rerun checks only that the computations reproduce. It does not review the physics assumptions, the conditional arithmetic ansatz, or the unresolved Narain, operator-lift and spectrum checks.
