#!/usr/bin/env python3
"""Exact, dependency-free checks for the bounded Z2 / Z2 workflow example.

The frozen arithmetic model is E8(-1) plus U plus U, with an untouched
second E8 subsystem. Root characters use the positive Euclidean E8 pairing;
the negative gauge norm is used only in the declared level-matching formula.
No full Narain embedding or heterotic spectrum is certified by this module.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import gcd
from pathlib import Path
import argparse
import json


SCHEMA_VERSION = 1
CONVENTIONS = {
    "gauge_lattice": "E8(-1); the second gauge factor is untouched",
    "gauge_norm": "qV = -sum(V_i^2)",
    "root_character": "exp(2*pi*i*alpha.dot(V)) in the positive Euclidean E8 coordinates",
    "torus_gram": [[0, 1, 0, 0], [1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]],
    "torus_norm": "qdelta = 2*delta_0*delta_1 + 2*delta_2*delta_3",
    "right_twist_norm": "qphi = sum(phi_i^2)",
    "level_matching": "N^2*(qV+qdelta-qphi) belongs to 2*N*Z",
    "local_projection": "16 abstract orthogonal A1 factors; scalar geometric signs (+,-,-)",
    "scope": "Conditional arithmetic ansatz and abstract local root projection only",
}


def lcm(a, b):
    return a * b // gcd(a, b)


def rational(value):
    # Refuse floating point: decimal approximation must not change congruences.
    if isinstance(value, bool) or not isinstance(value, (str, int, F)):
        raise ValueError("Exact numbers must be integers or rational strings, not floats/bools")
    return F(value)


def vector(values, length, field):
    if not isinstance(values, (list, tuple)) or len(values) != length:
        raise ValueError(f"{field} must have length {length}")
    return tuple(rational(x) for x in values)


def strings(values):
    return [str(x) for x in values]


def dot(a, b):
    if len(a) != len(b):
        raise ValueError("Pairing requires equal vector lengths")
    return sum((x * y for x, y in zip(a, b)), F(0))


def torus_norm(v):
    return 2 * v[0] * v[1] + 2 * v[2] * v[3]


def integral_vector(v):
    return all(x.denominator == 1 for x in v)


def e8_member(v):
    """E8 = integral or all half-integral coordinates, with even coordinate sum."""
    if len(v) != 8:
        return False
    v = tuple(rational(x) for x in v)
    same_coset = integral_vector(v) or all(x.denominator == 2 for x in v)
    return same_coset and sum(v) % 2 == 0


def denominator_order(v):
    n = 1
    for x in v:
        n = lcm(n, x.denominator)
    return n


def e8_shift_order(v):
    # N*(2V) must be integral. At that minimal N, the only remaining
    # constraints are common coordinate parity and an even coordinate sum.
    # At most two further factors of two enforce them.
    base = denominator_order(tuple(2 * x for x in v))
    for n in (base, 2 * base, 4 * base):
        if e8_member(tuple(n * x for x in v)):
            return n
    raise RuntimeError("E8 order bound was violated")


def a1_positive_roots():
    roots = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [F(0)] * 8
            r[i], r[i + 1] = F(1), F(sign)
            roots.append(tuple(r))
    return roots


def e8_roots():
    roots = []
    for i, j in combinations(range(8), 2):
        for a, b in product((-1, 1), repeat=2):
            r = [F(0)] * 8
            r[i], r[j] = F(a), F(b)
            roots.append(tuple(r))
    roots.extend(tuple(F(s, 2) for s in signs)
                 for signs in product((-1, 1), repeat=8)
                 if signs.count(-1) % 2 == 0)
    return roots


GEOMETRIES = {
    "all_fixed": {
        "formula": "(-z1,z2)",
        "matrix": [[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        "translation": [0, 0, 0, 0],
    },
    "translation_i_over_2": {
        "formula": "(-z1,z2+i/2)",
        "matrix": [[-1, 0, 0, 0], [0, -1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        "translation": [0, 0, 0, 1],
    },
    "coordinate_exchange": {
        "formula": "(-z2,-z1)",
        "matrix": [[0, 0, -1, 0], [0, 0, 0, -1], [-1, 0, 0, 0], [0, -1, 0, 0]],
        "translation": [0, 0, 0, 0],
    },
}


def geometry_orbits(action_name):
    if action_name not in GEOMETRIES:
        raise ValueError("Unknown geometric action")
    data = GEOMETRIES[action_name]
    def action(p):
        return tuple((sum(a * b for a, b in zip(row, p)) + t) % 2
                     for row, t in zip(data["matrix"], data["translation"]))
    labels = list(product(range(2), repeat=4))
    involution = all(action(action(p)) == p for p in labels)
    if not involution:
        raise RuntimeError("Geometric action did not square to identity")
    seen, orbits = set(), []
    for p in labels:
        if p not in seen:
            orbit = sorted(set((p, action(p))))
            seen.update(orbit)
            orbits.append([list(q) for q in orbit])
    return {
        "action": action_name, "formula": data["formula"],
        "fixed_components": sum(len(o) == 1 for o in orbits),
        "exchanged_pairs": sum(len(o) == 2 for o in orbits),
        "permutation_squares_to_identity": involution, "orbits": orbits,
    }


def geometry_preflight():
    return {key: geometry_orbits(key) for key in GEOMETRIES}


def local_weyl_audit():
    def mul(a, b):
        return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(2))
                           for j in range(2)) for i in range(2))
    def scale(n, a):
        return tuple(tuple(n * x for x in row) for row in a)
    def sub(a, b):
        return tuple(tuple(x - y for x, y in zip(ra, rb)) for ra, rb in zip(a, b))
    def bracket(a, b):
        return sub(mul(a, b), mul(b, a))
    w, h, x = ((0, 1), (-1, 0)), ((1, 0), (0, -1)), ((0, 1), (1, 0))
    basis = (w, h, x)
    def conjugate(a):
        return mul(mul(w, a), scale(-1, w))
    parities = []
    for b in basis:
        transformed = conjugate(b)
        parities.append(1 if transformed == b else -1 if transformed == scale(-1, b) else None)
    bracket_results = [conjugate(bracket(a, b)) == bracket(conjugate(a), conjugate(b))
                       for a in basis for b in basis]
    return {"representative": w, "square": mul(w, w), "basis": basis,
            "adjoint_parities": parities, "brackets_preserved": bracket_results,
            "scope": "Exact conjugation on sl2(C), the complexification of su(2)"}


def record(name, passed, evidence, scope):
    return {"name": name, "status": "PASS" if passed else "FAIL",
            "evidence": evidence, "scope": scope}


def unresolved(name, evidence):
    return {"name": name, "status": "UNRESOLVED", "evidence": evidence,
            "scope": "Complete heterotic construction"}


def _validate_case(case):
    if not isinstance(case, dict):
        raise ValueError("Candidate must be an object")
    if not isinstance(case.get("id"), str) or not case["id"]:
        raise ValueError("Candidate id must be a nonempty string")
    n = case.get("N")
    if isinstance(n, bool) or not isinstance(n, int) or not 1 <= n <= 64:
        raise ValueError("N must be an integer between 1 and 64")
    v = vector(case["V"], 8, "V")
    delta = vector(case["delta"], 4, "delta")
    phi = vector(case["phi"], 3, "phi")
    if any(x.denominator > 256 for x in v + delta + phi):
        raise ValueError("This bounded demo accepts denominators at most 256")
    target = case["target"]
    higgs = target["higgs_indices_zero_based"]
    if (not isinstance(higgs, list) or any(type(x) is not int or x not in range(16) for x in higgs)
            or len(set(higgs)) != len(higgs)):
        raise ValueError("Higgs indices must be distinct integers from 0 to 15")
    for key in ("fixed_components", "exchanged_pairs"):
        if type(target[key]) is not int or target[key] < 0:
            raise ValueError(f"Target {key} must be a nonnegative integer")
    if target["fixed_components"] + 2 * target["exchanged_pairs"] != 16:
        raise ValueError("Target component counts must account for 16 A1 singularities")
    return n, v, delta, phi, target, higgs


def evaluate_candidate(case):
    """Evaluate actual supplied data; malformed data is ERROR, never physics FAIL.

    scoped_status concerns the implemented checks. overall_status cannot be
    PASS because this demo does not implement full Narain and spectrum checks.
    """
    candidate_id = case.get("id", "<missing>") if isinstance(case, dict) else "<invalid>"
    try:
        n, v, delta, phi, target, higgs = _validate_case(case)
        geom = geometry_orbits(case["geometry_action"])
    except (KeyError, ValueError, TypeError, ZeroDivisionError) as exc:
        return {"id": candidate_id, "execution_status": "ERROR", "scoped_status": None,
                "overall_status": "UNRESOLVED", "checks": [],
                "error": f"{type(exc).__name__}: {exc}"}

    checks = []
    checks.append(record("geometry_target",
        (geom["fixed_components"], geom["exchanged_pairs"]) ==
        (target["fixed_components"], target["exchanged_pairs"]),
        {"computed": {k: geom[k] for k in ("fixed_components", "exchanged_pairs")},
         "claimed": {k: target[k] for k in ("fixed_components", "exchanged_pairs")}},
        "Permutation of the sixteen K3 orbifold singular points"))

    nv, ndelta = tuple(n * x for x in v), tuple(n * x for x in delta)
    checks.append(record("gauge_lattice_membership", e8_member(nv),
        {"N_V": strings(nv), "in_E8": e8_member(nv),
         "coordinate_sum": str(sum(nv))}, "The declared E8 gauge factor"))
    checks.append(record("torus_lattice_membership", integral_vector(ndelta),
        {"N_delta": strings(ndelta), "integral": integral_vector(ndelta)},
        "The declared U plus U integral basis"))
    orders = {"gauge": e8_shift_order(v), "torus_shift": denominator_order(delta),
              "right_twist": denominator_order(phi)}
    combined = lcm(lcm(orders["gauge"], orders["torus_shift"]), orders["right_twist"])
    checks.append(record("declared_shift_order", combined == n,
        {"declared_N": n, "computed_combined_order": combined, "factor_orders": orders},
        "Orders modulo the declared lattices; this is not the full vertex-operator lift"))
    ext = delta[2:]
    checks.append(record("external_translation",
        ext[0] % 1 == 0 and ext[1] % 1 == F(1, 2) and 2 * ext[0] * ext[1] == 0,
        {"external_coordinates": strings(ext), "norm": str(2 * ext[0] * ext[1]),
         "order_mod_Z2": denominator_order(ext)},
        "The fixed null order-two half-translation of this ansatz"))
    checks.append(record("right_twist_assignment", phi == (F(1, 2), F(1, 2), F(0)),
        {"supplied_phi": strings(phi), "frozen_phi": ["1/2", "1/2", "0"]},
        "The fixed right-moving twist representative of this arithmetic example"))

    phases = [dot(root, v) % 1 for root in a1_positive_roots()] + [F(0)] * 8
    expected_phases = [F(1, 2) if i in higgs else F(0) for i in range(16)]
    checks.append(record("local_root_action", phases == expected_phases,
        {"computed_positive_root_phases_mod_1": strings(phases),
         "target_positive_root_phases_mod_1": strings(expected_phases),
         "order_two_on_selected_roots": all(2 * p % 1 == 0 for p in phases)},
        "Abstract A1^8 plus A1^8 subsystem; the second E8 factor is untouched"))
    # For each A1 there is one Cartan phase zero and two opposite root phases.
    generator_phases = [F(0)] * 16 + [s * p % 1 for p in phases for s in (1, -1)]
    vector_dim = sum(p == 0 for p in generator_phases)
    scalar_dims = [sum((p + g) % 1 == 0 for p in generator_phases)
                   for g in (F(0), F(1, 2), F(1, 2))]
    h = len(higgs)
    target_vector, target_scalars = 48 - 2 * h, [48 - 2 * h, 2 * h, 2 * h]
    local_dimensions = {"computed_vector_dimension": vector_dim,
        "computed_scalar_dimensions": scalar_dims, "target_vector_dimension": target_vector,
        "target_scalar_dimensions": target_scalars,
        "target_origin_algebra": {"su2_factors": 16 - h, "u1_factors": h}}
    if geom["fixed_components"] != 16 or target["fixed_components"] != 16:
        checks.append(unresolved("local_projected_dimensions",
            {**local_dimensions, "reason": "This local field projection is implemented only for the all-fixed geometry"}))
    else:
        checks.append(record("local_projected_dimensions",
            vector_dim == target_vector and scalar_dims == target_scalars,
            local_dimensions, "Linear local ADE field projection; not the complete heterotic spectrum"))

    qv, qdelta, qphi = -dot(v, v), torus_norm(delta), dot(phi, phi)
    value, modulus = n * n * (qv + qdelta - qphi), 2 * n
    checks.append(record("level_matching", value % modulus == 0,
        {"qV": str(qv), "qdelta": str(qdelta), "qphi": str(qphi),
         "N2_qV": str(n * n * qv), "N2_qdelta": str(n * n * qdelta),
         "N2_qphi": str(n * n * qphi), "congruence_value": str(value),
         "modulus": modulus, "residue": str(value % modulus)},
        "The single written level-matching congruence in the frozen conventions"))

    bg = case.get("physical_background")
    background_note = "No full background was supplied" if bg is None else (
        "Background data was supplied but is not validated by this bounded checker")
    checks.extend([
        unresolved("narain_embedding", {"reason": background_note,
            "required": "Integral Narain basis, Gram form, gluing, moduli/Wilson lines and actual enhanced roots"}),
        unresolved("operator_lift", {"reason": "No vertex-operator lift or all-sector consistency calculation is implemented",
            "required": "Cocycles/phases and consistency of all powers and sectors"}),
        unresolved("complete_spectrum_branch_match", {
            "reason": "Local subsystem phases and one congruence do not determine full massless spectrum",
            "required": "Full P dot (V+delta), twisted and bulk states, and the branch dictionary"}),
    ])
    scoped = checks[:-3]
    scoped_status = "FAIL" if any(c["status"] == "FAIL" for c in scoped) else (
        "UNRESOLVED" if any(c["status"] == "UNRESOLVED" for c in scoped) else "PASS")
    roots = e8_roots()
    retained = sum(dot(p, v) % 1 == 0 for p in roots)
    return {"id": case["id"], "execution_status": "OK", "scoped_status": scoped_status,
            "overall_status": "FAIL" if scoped_status == "FAIL" else "UNRESOLVED",
            "checks": checks, "diagnostics": {
                "unbroken_E8_root_count": len(roots), "roots_retained_by_V_on_unbroken_E8": retained,
                "roots_retained_in_first_A1_8_subsystem": 2 * sum(p == 0 for p in phases[:8]),
                "interpretation": "Different ambient root sets give different invariants. This is not the physical Narain spectrum."}}


def finite_shift_scan(N, V, phi):
    """Exhaust the N^2 raw residue pairs in the fixed null external-shift ansatz."""
    if type(N) is not int or N not in (2, 4):
        raise ValueError("This reference scan supports N=2 or N=4")
    v, phi = vector(V, 8, "V"), vector(phi, 3, "phi")
    entries = []
    for a, b in product(range(N), repeat=2):
        delta = (F(a, N), F(b, N), F(0), F(1, 2))
        value = N * N * (-dot(v, v) + torus_norm(delta) - dot(phi, phi))
        entries.append({"a": a, "b": b, "delta": strings(delta),
                        "residue": str(value % (2 * N)), "passes_congruence": value % (2 * N) == 0})
    return {"N": N, "raw_pair_count": N * N,
            "surviving_pairs": [[e["a"], e["b"]] for e in entries if e["passes_congruence"]],
            "all_pairs": entries,
            "scope": "Raw arithmetic representatives, not inequivalent backgrounds or verified duals"}


def run_suite(fixtures):
    if not isinstance(fixtures, dict) or fixtures.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported fixture schema")
    cases = fixtures["cases"]
    if not isinstance(cases, list):
        raise ValueError("cases must be a list")
    results = [evaluate_candidate(case) for case in cases]
    return {"schema_version": SCHEMA_VERSION,
        "title": "Z2 / Z2: a bounded proposal-and-check workflow",
        "conventions": CONVENTIONS, "geometry_preflight": geometry_preflight(),
        "local_weyl_audit": local_weyl_audit(), "cases": results,
        "reference_scans": {
            case["id"]: finite_shift_scan(case["N"], case["V"], case["phi"])
            for case, result in zip(cases, results)
            if isinstance(case, dict) and case.get("role") == "reference"
            and result["execution_status"] == "OK" and case["N"] in (2, 4)},
        "summary": {
            "case_count": len(results),
            "execution_errors": sum(r["execution_status"] == "ERROR" for r in results),
            "scoped_pass": sum(r["scoped_status"] == "PASS" for r in results),
            "scoped_fail": sum(r["scoped_status"] == "FAIL" for r in results),
            "overall_unresolved": sum(r["overall_status"] == "UNRESOLVED" for r in results),
            "overall_fail": sum(r["overall_status"] == "FAIL" for r in results),
            "verified_duals": 0,
        },
        "review_status": "Deterministic computational results; independent human scientific review is not asserted",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    parser.add_argument("--fixtures", type=Path, default=here / "fixtures.json")
    parser.add_argument("--output", type=Path, default=here / "results.json")
    args = parser.parse_args()
    try:
        result = run_suite(json.loads(args.fixtures.read_text()))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(2, f"Execution error: {exc}\n")
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2))
    if result["summary"]["execution_errors"]:
        parser.exit(2, "One or more fixtures could not be evaluated.\n")


if __name__ == "__main__":
    main()
