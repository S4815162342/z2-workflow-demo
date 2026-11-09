#!/usr/bin/env python3
"""Check a model proposal against the frozen example inputs.

Without options, this checks the archived proposal in
logs/raw_model_response.json and writes logs/proposal_checks.json.
Use --proposal to check another answer (for example from a different model)
without touching the archived files.
"""
from copy import deepcopy
from pathlib import Path
import argparse
import json
from checker import evaluate_candidate

REQUIRED = ('N', 'V', 'delta', 'phi')


def load_proposal(path):
    """Read a JSON proposal. Tolerates a ```json ... ``` fence around it,
    as models often add one when the answer is pasted from a chat."""
    text = path.read_text().strip()
    if text.startswith('```'):
        lines = text.splitlines()[1:]
        if lines and lines[-1].strip().startswith('```'):
            lines = lines[:-1]
        text = '\n'.join(lines)
    proposal = json.loads(text)
    if not isinstance(proposal, dict):
        raise ValueError('the proposal must be a JSON object')
    missing = [key for key in REQUIRED if key not in proposal]
    if missing:
        raise ValueError('the proposal is missing ' + ', '.join(missing))
    return proposal


def main():
    here = Path(__file__).resolve().parent
    archived = here / 'logs/raw_model_response.json'
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--proposal', type=Path, default=archived,
                        help='JSON file with keys N, V, delta, phi (default: the archived proposal)')
    parser.add_argument('--output', type=Path, default=None,
                        help='where to write the check record (default: logs/proposal_checks.json '
                             'for the archived proposal, otherwise <proposal>.checks.json next to it)')
    args = parser.parse_args()

    is_archived = args.proposal.resolve() == archived
    output = args.output or (here / 'logs/proposal_checks.json' if is_archived
                             else args.proposal.with_suffix('.checks.json'))

    try:
        proposal = load_proposal(args.proposal)
    except (OSError, ValueError) as exc:
        parser.exit(2, f'Could not read {args.proposal}: {exc}\n')

    fixtures = json.loads((here / 'fixtures.json').read_text())
    case = deepcopy(fixtures['cases'][0])
    case['id'] = 'logged_model_proposal' if is_archived else 'proposal:' + args.proposal.name
    for key in REQUIRED:
        case[key] = proposal[key]
    result = evaluate_candidate(case)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({key: result[key] for key in ('id', 'execution_status', 'scoped_status', 'overall_status')}, indent=2))
    if not is_archived or args.output:
        print(f'Check record written to {output}')
    if result['execution_status'] != 'OK' or result['scoped_status'] != 'PASS':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
