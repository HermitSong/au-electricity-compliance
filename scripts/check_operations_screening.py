"""Replay a private screening report; success proves integrity, not legal accuracy."""
import argparse
import json
from pathlib import Path

from operations_screening import MAX_REPORT_BYTES, load_json, read_limited, validate_screening


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--transcript', type=Path, required=True)
    parser.add_argument('--context', type=Path, required=True)
    parser.add_argument('--proposals', type=Path)
    args = parser.parse_args(argv)
    try:
        errors = validate_screening(load_json(args.report, MAX_REPORT_BYTES), read_limited(args.transcript), load_json(args.context),
                                    load_json(args.proposals) if args.proposals else None)
    except (ValueError, OSError, TypeError, KeyError, RecursionError):
        errors = ['Invalid, stale or mismatched screening input.']
    print(json.dumps({'integrity_passed': not errors, 'legal_accuracy_verified': False,
                      'may_execute': False, 'errors': errors}))
    return 2 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
