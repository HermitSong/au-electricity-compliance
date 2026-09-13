"""Apply only explicitly selected, reviewed status overrides; preserve all other records."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--event-id', required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    override = json.loads((root / 'data/event-quality-overrides.json').read_text(encoding='utf-8-sig'))['overrides'][args.event_id]
    permitted = {'status', 'case_status_note', 'record_reviewed_at'}
    if set(override) != permitted:
        raise ValueError('Status correction requires only status, source-backed note and review date')
    path = root / 'data/enforcement-events-full.jsonl'
    lines = path.read_text(encoding='utf-8-sig').splitlines()
    matches = []
    for index, line in enumerate(lines):
        row = json.loads(line)
        if row['event_id'] == args.event_id:
            matches.append(index)
            lines[index] = json.dumps({**row, **override}, ensure_ascii=True, separators=(',', ':'))
    if len(matches) != 1:
        raise ValueError('Expected exactly one canonical event')
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Applied reviewed status to {args.event_id}; regenerate temporal links and search index.')


if __name__ == '__main__':
    main()
