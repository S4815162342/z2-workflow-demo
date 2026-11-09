# Playbook: one bounded proposal-and-check cycle

## 1. Fix the input before proposing a shift

The geometric K3 orbifold is `T4/G`, with `G = Z2` acting as `(z1,z2) -> (-z1,-z2)` on the square torus. Its sixteen singular points are labelled by four bits. The main example uses the further action `(z1,z2) -> (-z1,z2)` and the external action `(y1,y2,y3) -> (y1+1/2,-y2,-y3)`. All sixteen singular components are fixed. One component is assigned Higgs type and fifteen Coulomb type.

The label `higgs_indices_zero_based: [6]` identifies `e7+e8` in the chosen ordered abstract root frame. It is a bookkeeping choice, not a constructed map from a particular geometric singular point into the full Narain lattice.

Freeze the `E8` coordinate definition, the positive Euclidean pairing used for root characters, the negative gauge norm used in the written congruence, the `U + U` Gram matrix, the right twist and the external half-translation. The conditional arithmetic conventions are recorded in `checker.CONVENTIONS` and in every results file. Independent scientific review of this contract is a separate checkpoint in `HUMAN_REVIEW.md`.

## 2. Obtain and preserve a model proposal

Supply the frozen target and permitted ansatz to the model. Request exact rational coordinates, a declared order and an explanation. Preserve the prompt and raw response before any corrections. Record the model identifier when exposed by the runtime; do not guess a more specific model version.

The demonstration's recorded proposal is a fresh response to its supplied benchmark prompt. The reference example and expected test outcomes are already known to the project. This is a reproduction and workflow demonstration, not a claim of a newly discovered dual. Future reruns need not elicit identical prose or coordinates: verify saved proposed data with the deterministic checker.

## 3. Evaluate the proposal

Insert the proposed `V`, `delta`, `N` and `phi` into a copy of the frozen target record, preserving the target and conventions. Call `evaluate_candidate(case)`. Inspect the computed evidence for every check, including checks that pass. Distinguish the local root action from the order modulo the whole declared lattice.

For the main representative, `V=(0,0,0,0,0,0,1/4,1/4)`, selected roots have order-two phases but `2V` is outside `E8`; `4V` is inside. The torus representative is `delta=(1/4,1/4;0,1/2)`. In the declared signs, the written level-matching expression is `-8`, divisible by `2N=8`.

The exact reference scan exhausts the sixteen allowed `(a,b)` residue pairs. It checks completeness only within that frozen ansatz, not over all embeddings, lifts or physical backgrounds.

## 4. Challenge the checker

Run all six fixtures. The four invalid fixtures intentionally introduce: a geometric-target mismatch; an incorrect declared order; failure of `E8` membership; and an incorrect compensating shift. They are labelled `seeded_invalid: true`. They are tests of the checker, not claimed spontaneous model errors. One mutation may fail several checks.

Use `python3 -m unittest -v` to check the evaluator on independent expected values and malformed inputs. Debug software errors separately from candidate failures. Do not suppress an exception and present it as an obstruction in the physical model.

## 5. Review local physics and missing information

The selected local adjoint signs are `(+,-,-)`, with one invariant Cartan generator and two odd charged generators. Combining them with scalar geometric signs `(+,-,-)` gives local scalar dimensions `(1,2,2)`. Adding fifteen untouched factors gives vector dimension `46` and scalar dimensions `(46,2,2)`; the local origin algebra is `su(2)^15 + u(1)`.

These are local ADE-sector statements. The intended Higgs component is an `SO(2)` theory with a hypermultiplet in the two-dimensional vector representation. Identifying its full heterotic matter sector requires more than counting these local components.

The actual Narain roots may have momentum, winding or Wilson-line components, and the torus shift can affect their phases. `P dot (V+delta)`, operator lifts, all relevant sectors and branch matching remain unresolved. Giving the evaluator an unvalidated background object does not promote these checks to `PASS`.

## 6. Record the outcome

Keep the original proposal, check output, any corrected proposal and the explanation for each correction. Record computational acceptance separately from independent human scientific acceptance. The reference data should pass the named checks while remaining unresolved overall; the seeded invalid fixtures should fail with explicit evidence.

Complete the human review sheet only after actually carrying out the listed review. The demonstration produces an inspectable input-to-output record and a reproducible set of exact checks.
