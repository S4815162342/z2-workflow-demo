#!/usr/bin/env python3
"""Reference tests and adversarial fixtures for the bounded exact checker.

Expected values are kept here, outside the candidate evaluator. A planted
invalid input passing these tests means it was correctly rejected, not that
the input describes a valid construction.
"""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import unittest

import checker


HERE = Path(__file__).resolve().parent


def load_fixtures():
    return json.loads((HERE / "fixtures.json").read_text())


def by_name(result):
    return {c["name"]: c for c in result["checks"]}


class ExactCheckerTests(unittest.TestCase):
    def setUp(self):
        self.fixtures = load_fixtures()
        self.baseline = self.fixtures["cases"][0]

    def test_geometry_source_table(self):
        # Expected orbit counts for the three K actions, fixed independently of the checker.
        expected = {"all_fixed": (16, 0), "translation_i_over_2": (0, 8),
                    "coordinate_exchange": (4, 6)}
        for name, pair in expected.items():
            result = checker.geometry_orbits(name)
            self.assertEqual((result["fixed_components"], result["exchanged_pairs"]), pair)
            points = [tuple(p) for orbit in result["orbits"] for p in orbit]
            self.assertEqual(len(points), 16)
            self.assertEqual(len(set(points)), 16)

    def test_E8_cosets_and_parity(self):
        self.assertTrue(checker.e8_member([1, 1, 0, 0, 0, 0, 0, 0]))
        self.assertFalse(checker.e8_member([1, 0, 0, 0, 0, 0, 0, 0]))
        self.assertTrue(checker.e8_member([F(1, 2)] * 8))
        self.assertFalse(checker.e8_member([F(-1, 2)] + [F(1, 2)] * 7))
        self.assertFalse(checker.e8_member([F(1, 2), F(1, 2)] + [0] * 6))
        self.assertFalse(checker.e8_member([F(1, 3)] * 8))

    def test_E8_root_inventory(self):
        roots = checker.e8_roots()
        self.assertEqual(len(set(roots)), 240)
        self.assertTrue(all(checker.dot(r, r) == 2 for r in roots))
        self.assertTrue(all(checker.e8_member(r) for r in roots))
        self.assertTrue(all(tuple(-x for x in r) in roots for r in roots))

    def test_order_vs_membership_by_explicit_multiples(self):
        # The independent oracle searches every positive multiple, rather
        # than using the denominator/parity shortcut in e8_shift_order().
        for denominator in (2, 3, 4, 6):
            for a in range(denominator):
                for b in range(denominator):
                    v = (F(a, denominator), F(b, denominator)) + (F(0),) * 6
                    brute = next(n for n in range(1, 2 * denominator + 1)
                                 if checker.e8_member(tuple(n * x for x in v)))
                    self.assertEqual(checker.e8_shift_order(v), brute)

    def test_local_weyl_conjugation(self):
        audit = checker.local_weyl_audit()
        self.assertEqual(audit["square"], ((-1, 0), (0, -1)))
        self.assertEqual(audit["adjoint_parities"], [1, -1, -1])
        self.assertEqual(audit["brackets_preserved"], [True] * 9)

    def test_reference_one_higgs_values(self):
        result = checker.evaluate_candidate(self.baseline)
        checks = by_name(result)
        self.assertEqual(result["scoped_status"], "PASS")
        self.assertEqual(result["overall_status"], "UNRESOLVED")
        self.assertEqual(checks["declared_shift_order"]["evidence"]["computed_combined_order"], 4)
        self.assertEqual(checks["local_projected_dimensions"]["evidence"]["computed_vector_dimension"], 46)
        self.assertEqual(checks["local_projected_dimensions"]["evidence"]["computed_scalar_dimensions"], [46, 2, 2])
        lm = checks["level_matching"]["evidence"]
        self.assertEqual((lm["N2_qV"], lm["N2_qdelta"], lm["N2_qphi"]), ("-2", "2", "8"))
        self.assertEqual((lm["congruence_value"], lm["residue"]), ("-8", "0"))
        self.assertEqual(result["diagnostics"]["roots_retained_by_V_on_unbroken_E8"], 126)
        self.assertEqual(result["diagnostics"]["roots_retained_in_first_A1_8_subsystem"], 14)

    def test_reference_all_coulomb_values(self):
        result = checker.evaluate_candidate(self.fixtures["cases"][1])
        checks = by_name(result)
        self.assertEqual(result["scoped_status"], "PASS")
        self.assertEqual(result["overall_status"], "UNRESOLVED")
        self.assertEqual(checks["local_projected_dimensions"]["evidence"]["computed_scalar_dimensions"], [48, 0, 0])
        self.assertEqual(checks["declared_shift_order"]["evidence"]["computed_combined_order"], 2)

    def test_four_seeded_inputs_fail_specific_checks(self):
        required = {"seeded_geometry_mismatch": "geometry_target",
                    "seeded_wrong_order": "declared_shift_order",
                    "seeded_lattice_failure": "gauge_lattice_membership",
                    "seeded_level_matching_failure": "level_matching"}
        for case in self.fixtures["cases"][2:]:
            with self.subTest(case=case["id"]):
                result = checker.evaluate_candidate(case)
                self.assertEqual(result["execution_status"], "OK")
                self.assertEqual(result["scoped_status"], "FAIL")
                self.assertEqual(by_name(result)[required[case["id"]]]["status"], "FAIL")
        lm_case = checker.evaluate_candidate(self.fixtures["cases"][-1])
        self.assertEqual(by_name(lm_case)["level_matching"]["evidence"]["residue"], "4")

    def test_wrong_geometry_does_not_claim_local_projection(self):
        result = checker.evaluate_candidate(self.fixtures["cases"][2])
        self.assertEqual(by_name(result)["local_projected_dimensions"]["status"], "UNRESOLVED")

    def test_exhaustive_scan_matches_independent_residue_formula(self):
        baseline = self.baseline
        scan = checker.finite_shift_scan(4, baseline["V"], baseline["phi"])
        self.assertEqual(scan["raw_pair_count"], 16)
        self.assertEqual(scan["surviving_pairs"], [[1, 1], [3, 3]])
        for e in scan["all_pairs"]:
            # By hand: -2+2ab-8 = 2ab-10, divisible by 8 iff ab=1 mod4.
            self.assertEqual(e["passes_congruence"], e["a"] * e["b"] % 4 == 1)
        control = self.fixtures["cases"][1]
        self.assertEqual(checker.finite_shift_scan(2, control["V"], control["phi"])["surviving_pairs"], [[1, 1]])

    def test_changed_candidate_is_recomputed(self):
        changed = deepcopy(self.baseline)
        changed["delta"][:2] = ["3/4", "3/4"]
        self.assertEqual(checker.evaluate_candidate(changed)["scoped_status"], "PASS")
        changed["delta"][0] = "0"
        result = checker.evaluate_candidate(changed)
        self.assertEqual(by_name(result)["level_matching"]["status"], "FAIL")
        self.assertEqual(by_name(result)["level_matching"]["evidence"]["qdelta"], "0")

    def test_undeclared_twist_cannot_pass_frozen_example(self):
        changed = deepcopy(self.baseline)
        changed["phi"] = ["0", "0", "0"]
        result = checker.evaluate_candidate(changed)
        self.assertEqual(by_name(result)["right_twist_assignment"]["status"], "FAIL")
        self.assertEqual(result["scoped_status"], "FAIL")

    def test_incomplete_physical_inputs_stay_unresolved(self):
        for background in (None, {}, {"claim": "verified"}):
            changed = deepcopy(self.baseline)
            changed["physical_background"] = background
            result = checker.evaluate_candidate(changed)
            checks = by_name(result)
            for name in ("narain_embedding", "operator_lift", "complete_spectrum_branch_match"):
                self.assertEqual(checks[name]["status"], "UNRESOLVED")
            self.assertEqual(result["overall_status"], "UNRESOLVED")

    def test_malformed_input_is_execution_error(self):
        invalid = [None, {}, {"id": "missing_fields"}]
        for modification in (("V", [0] * 7), ("N", True), ("N", 0),
                             ("delta", [0.25, "1/4", "0", "1/2"]),
                             ("V", ["1/0"] + ["0"] * 7),
                             ("geometry_action", "unknown")):
            changed = deepcopy(self.baseline)
            changed[modification[0]] = modification[1]
            invalid.append(changed)
        for case in invalid:
            result = checker.evaluate_candidate(case)
            self.assertEqual(result["execution_status"], "ERROR")
            self.assertIsNone(result["scoped_status"])
            self.assertEqual(result["overall_status"], "UNRESOLVED")

    def test_suite_summary_and_determinism(self):
        result = checker.run_suite(self.fixtures)
        self.assertEqual(result["summary"], {"case_count": 6, "execution_errors": 0,
            "scoped_pass": 2, "scoped_fail": 4, "overall_unresolved": 2,
            "overall_fail": 4, "verified_duals": 0})
        self.assertEqual(json.dumps(result, sort_keys=True),
                         json.dumps(checker.run_suite(self.fixtures), sort_keys=True))

    def test_suite_keeps_malformed_case_as_error(self):
        result = checker.run_suite({"schema_version": 1, "cases": [None,
            {"id": "broken_reference", "role": "reference"}]})
        self.assertEqual(result["summary"]["execution_errors"], 2)
        self.assertEqual(result["summary"]["scoped_fail"], 0)
        self.assertEqual(result["reference_scans"], {})


if __name__ == "__main__":
    unittest.main(verbosity=2)
