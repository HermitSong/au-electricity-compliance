"""Validate and add evidence deltas without replacing older immutable objects."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import uuid

from collect_source_originals import discover, now, read_jsonl, rebuild_outputs, select_manifest_rows
from merge_source_recovery import fingerprint
from validate_source_originals import check_artifacts


MUTABLE = ('source-originals/manifest.jsonl', 'source-originals/search.sqlite3',
           'data/source-original-inventory.jsonl', 'data/source-original-gap-queue.jsonl',
           'data/source-original-summary.json', 'review/results/original-source-collection-report.md',
           'review/results/evidence-batch-merge.json')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def merge_metadata(entries, row):
    url = row['canonical_url']
    clean = {k: deepcopy(v) for k, v in row.items()
             if not k.startswith('latest_') and k != 'has_research_text'}
    if url not in entries:
        entries[url] = {k: clean[k] for k in (
            'canonical_url', 'references', 'source_family_ids', 'discovery_depth',
            'discovered_from', 'link_label', 'source_index_evidence', 'document_role',
            'same_path_other_urls', 'version_identity_status', 'relevance_status') if k in clean}
    target = entries[url]
    for key in ('references', 'source_family_ids', 'discovered_from', 'source_index_evidence'):
        target.setdefault(key, [])
        for value in clean.get(key, []):
            if value not in target[key]:
                target[key].append(value)
    target['discovery_depth'] = min(target.get('discovery_depth', 0), clean.get('discovery_depth', 0))


def prepare(root, batches, enumeration):
    root = root.resolve()
    if not (root / 'source-originals/objects').resolve().is_relative_to(root):
        raise ValueError('Destination object directory escapes archive root')
    prior = read_jsonl(root / 'source-originals/manifest.jsonl')
    existing = {fingerprint(row) for row in prior}
    objects, pending, errors = {}, [], []
    entries = {row['canonical_url']: {k: v for k, v in row.items()
               if not k.startswith('latest_') and k != 'has_research_text'}
               for row in read_jsonl(root / 'data/source-original-inventory.jsonl')}
    for batch in batches:
        batch = batch.resolve()
        if batch == root or batch.is_relative_to(root):
            raise ValueError('Evidence delta must be outside the destination archive')
        if not (batch / 'source-originals/objects').resolve().is_relative_to(batch):
            raise ValueError('Delta object directory escapes its root')
        checked = set()
        logs = [batch / 'source-originals/manifest.jsonl',
                *sorted((batch / 'source-originals').glob('recovery-*.jsonl'))]
        final_ocr = batch / 'source-originals/recovery-priority-ocr.jsonl'
        if final_ocr.exists():
            # Its records retain both engines' objects. Do not let log-name order
            # replace the completed handoff with an earlier single-engine text.
            logs = [final_ocr]
        for log in logs:
            for row in read_jsonl(log):
                if row.get('current_law_release') is not False or row.get('legal_review_status') != 'not-reviewed':
                    errors.append('Acquisition delta must remain unreviewed: ' + row['canonical_url'])
                if row.get('capture_status') in {'bytes-preserved', 'browser-text-preserved'} and not row.get('snapshot_path'):
                    errors.append('Preserved outcome is missing its primary artifact')
                check_artifacts(batch, row, checked, errors)
                merge_metadata(entries, row)
                for child in discover(row, {'aemo.com.au'}, 2):
                    merge_metadata(entries, child)
                identity = fingerprint(row)
                if identity not in existing:
                    pending.append({**row, 'evidence_import_id': identity, 'evidence_imported_at': now()})
                    existing.add(identity)
        for relative, expected in checked:
            source = (batch / relative).resolve()
            target = (root / relative).resolve()
            if not target.is_relative_to((root / 'source-originals/objects').resolve()):
                errors.append('Destination path escapes original archive')
            elif target.exists() and digest(target) != expected:
                errors.append('Existing immutable destination differs: ' + relative)
            elif relative in objects and objects[relative][1] != expected:
                errors.append('Delta objects disagree: ' + relative)
            objects[relative] = (source, expected)
    for row in enumeration:
        for evidence in row.get('source_index_evidence', []):
            relative, expected = evidence['snapshot_path'], evidence['sha256']
            source = objects.get(relative, ((root / relative).resolve(), None))[0]
            allowed = any(source.is_relative_to((p.resolve() / 'source-originals/objects').resolve())
                          for p in [root, *batches])
            if not allowed or not source.is_file() or digest(source) != expected:
                errors.append('Source-index enumeration evidence is missing or corrupt')
        merge_metadata(entries, row)
    if errors:
        raise ValueError('; '.join(errors))
    return prior, pending, entries, objects


def merge(root, batches, enumeration, legacy_root, dry_run=False):
    root = root.resolve()
    original_manifest = digest(root / 'source-originals/manifest.jsonl')
    before_inventory = read_jsonl(root / 'data/source-original-inventory.jsonl')
    baseline = json.loads((root / 'data/source-original-summary.json').read_text(encoding='utf-8-sig'))
    prior, pending, entries, objects = prepare(root, batches, enumeration)
    _, before_text = select_manifest_rows(prior)
    _, after_text = select_manifest_rows(prior + pending)
    known = {row['canonical_url'] for row in before_inventory}
    prior_missing = known - set(before_text)
    report = {'generated_at': now(), 'dry_run': dry_run, 'manifest_rows_to_append': len(pending),
              'validated_delta_object_count': len(objects),
              'new_object_count': sum(not (root / relative).exists() for relative in objects),
              'inventory_urls_before': len(known), 'inventory_urls_after': len(entries),
              'research_text_urls_before': len(before_text), 'research_text_urls_after': len(after_text),
              'previously_missing_urls_recovered': len(prior_missing & set(after_text)),
              'previously_missing_urls_still_without_text': len(prior_missing - set(after_text)),
              'newly_enumerated_urls_with_text': len((set(entries) - known) & set(after_text)),
              'newly_enumerated_urls_without_text': len((set(entries) - known) - set(after_text)),
              'new_unique_snapshot_hashes': len({r['sha256'] for r in pending if r.get('sha256')} -
                                                {r['sha256'] for r in prior if r.get('sha256')}),
              'legal_review_status': 'not-reviewed', 'current_law_release': False,
              'boundaries': ['URL, file, event, finding and current legal applicability are different counts.',
                             'All enumerated URLs, including pending acquisitions, remain in the denominator.',
                             'Technical event reports do not establish a contravention.',
                             'Byte identity and successful extraction do not certify semantic accuracy or nationwide completeness.']}
    if dry_run:
        return report
    if digest(root / 'source-originals/manifest.jsonl') != original_manifest:
        raise ValueError('Destination manifest changed during validation; retry against the current archive')
    backup = root / 'review/backups' / ('evidence-' + uuid.uuid4().hex)
    backup.mkdir(parents=True)
    present = []
    for relative in MUTABLE:
        source = root / relative
        if source.exists():
            target = backup / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            present.append(relative)
    report['backup_path'] = backup.relative_to(root).as_posix()
    try:
        for relative, (source, expected) in objects.items():
            target = root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                # Exclusive creation prevents overwriting any concurrent immutable object.
                with source.open('rb') as src, target.open('xb') as dest:
                    shutil.copyfileobj(src, dest)
            if digest(target) != expected:
                raise ValueError('Copied immutable object failed SHA-256 validation')
        with (root / 'source-originals/manifest.jsonl').open('a', encoding='utf-8', newline='\n') as handle:
            for row in pending:
                handle.write(json.dumps(row, ensure_ascii=True) + '\n')
        rebuild_outputs(root, entries, baseline['initial_seed_url_count'], now(), legacy_root)
        output = root / 'review/results/evidence-batch-merge.json'
        output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    except Exception:
        for relative in present:
            shutil.copy2(backup / relative, root / relative)
        raise
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--batch', type=Path, action='append', required=True)
    parser.add_argument('--enumeration', type=Path, required=True)
    parser.add_argument('--legacy-root', type=Path)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    print(json.dumps(merge(args.root, args.batch, read_jsonl(args.enumeration),
                           args.legacy_root, args.dry_run), indent=2))


if __name__ == '__main__':
    main()
