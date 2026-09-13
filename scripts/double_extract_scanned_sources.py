"""Keep independent English OCR and disagreement evidence for scanned originals."""
import argparse
from difflib import SequenceMatcher
import hashlib
import json
from pathlib import Path
import re
import sys
from collect_source_originals import now, read_jsonl, save_object


def critical_tokens(text):
    return sorted(set(re.findall(r'\$?\d[\d,./:-]*[A-Za-z]*', text)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--ocr-packages', type=Path, required=True)
    parser.add_argument('--tessdata', type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(args.ocr_packages.resolve()))
    from tesserocr import PyTessBaseAPI, PSM, tesseract_version
    root = args.root.resolve()
    log = root / 'source-originals/recovery-ocr-double.jsonl'
    done = {row['canonical_url'] for row in read_jsonl(log)}
    queue = [row for row in read_jsonl(root / 'source-originals/recovery-ocr.jsonl')
             if row['recovery_status'] == 'captured' and row['canonical_url'] not in done]
    print(json.dumps({'queued_documents': len(queue)}), flush=True)
    with PyTessBaseAPI(path=str(args.tessdata.resolve()), lang='eng', psm=PSM.AUTO) as api, log.open('a', encoding='utf-8', newline='\n') as handle:
        for prior in queue:
            first = {unit['locator']: unit['text'] for unit in json.loads((root / prior['text_path']).read_bytes())}
            pages = json.loads((root / prior['ocr_pages_path']).read_bytes())
            units, comparison = [], []
            for page in pages:
                source = root / page['image_path']
                if hashlib.sha256(source.read_bytes()).hexdigest() != page['image_sha256']:
                    raise ValueError('OCR page image hash mismatch')
                api.SetImageFile(str(source))
                text = api.GetUTF8Text().strip()
                tsv_path, tsv_hash = save_object(root, api.GetTSVText(0).encode(), '.tsv')
                locator = f"page:{page['page']}"
                a, b = first.get(locator, ''), text
                units.append({'locator': locator, 'text': text or a})
                comparison.append({'page': page['page'], 'image_path': page['image_path'], 'image_sha256': page['image_sha256'],
                                   'tesseract_word_boxes_path': tsv_path, 'tesseract_word_boxes_sha256': tsv_hash,
                                   'tesseract_mean_confidence': api.MeanTextConf(),
                                   'alphanumeric_similarity': SequenceMatcher(None, re.sub(r'\W', '', a.lower()), re.sub(r'\W', '', b.lower()), autojunk=False).ratio(),
                                   'tokens_only_in_first': sorted(set(critical_tokens(a)) - set(critical_tokens(b))),
                                   'tokens_only_in_second': sorted(set(critical_tokens(b)) - set(critical_tokens(a))),
                                   'status': 'unreviewed-engine-disagreement-not-legal-validation'})
            text_path, text_hash = save_object(root, (json.dumps(units, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
            compare_path, compare_hash = save_object(root, (json.dumps(comparison, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
            row = {**prior, 'extraction_refreshed_at': now(), 'text_path': text_path, 'text_sha256': text_hash,
                   'text_character_count': sum(len(unit['text']) for unit in units),
                   'alternative_text_path': prior['text_path'], 'alternative_text_sha256': prior['text_sha256'],
                   'ocr_comparison_path': compare_path, 'ocr_comparison_sha256': compare_hash,
                   'ocr_engines': ['rapidocr-onnxruntime-1.4.4', tesseract_version()],
                   'text_selection_note': 'English Tesseract preferred after sample visual inspection; both outputs remain unverified and both are preserved.',
                   'pages_without_text': [page['page'] for page in pages if not units[page['page'] - 1]['text']],
                   'ocr_review_status': 'independent-extractions-compared; visual-critical-field-review-required'}
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            handle.flush()
            print(json.dumps({'completed': row['canonical_url'], 'pages': len(pages), 'critical_token_disagreement_pages': sum(bool(r['tokens_only_in_first'] or r['tokens_only_in_second']) for r in comparison)}), flush=True)


if __name__ == '__main__':
    main()
