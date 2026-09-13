"""Run the explicit public-edition test profile without rewriting archive tests."""
import argparse
import json
from pathlib import Path
import platform
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    profile = json.loads((ROOT / 'review/public-release-test-profile.json').read_text('utf-8'))
    omitted = profile['archive_dependent_tests']
    tests = list(flatten(unittest.defaultTestLoader.discover(str(ROOT / 'review/tests'))))
    missing = set(omitted) - {test.id() for test in tests}
    if missing:
        raise ValueError('Stale public test profile: ' + ', '.join(sorted(missing)))
    selected = [test for test in tests if test.id() not in omitted]
    ids = [test.id() for test in selected]
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    report = {
        'schema_version': '1.0', 'scope': profile['scope'],
        'python_version': platform.python_version(), 'platform': platform.system(),
        'discovered': len(tests), 'archive_dependent_not_run': omitted,
        'selected_test_ids': ids, 'tests_run': result.testsRun,
        'failures': [test.id() for test, _ in result.failures],
        'errors': [test.id() for test, _ in result.errors],
        'skipped': [{'test': test.id(), 'reason': (
            'Symlink creation unavailable on this runtime (Windows privilege requirement).'
            if reason.startswith('Symlink creation unavailable:') else
            'Test prerequisite unavailable; inspect the private local run log for details.')}
            for test, reason in result.skipped],
        'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
        'successful': result.wasSuccessful(), 'legal_accuracy_established': False,
    }
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    raise SystemExit(main())
