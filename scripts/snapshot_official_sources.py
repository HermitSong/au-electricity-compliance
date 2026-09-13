"""Legacy snapshot admission helper; standalone network acquisition is retired."""
import sys


def known_access_interstitial(data: bytes, content_type: str) -> bool:
    if 'html' not in content_type.lower():
        return False
    lowered = data.lower()
    return (b'<script' in lowered and b'triggerinterstitialchallenge' in lowered
            and b'/_sec/verify?provider=interstitial' in lowered)


def capture(*args, **kwargs):
    raise ValueError('Legacy acquisition is disabled; use the permission-gated source collector')


def main():
    print('This legacy network command is disabled. Read '
          'skills/au-lawful-source-acquisition/SKILL.md and use '
          'collect_source_originals.py with a private output directory and reviewed permissions.', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
