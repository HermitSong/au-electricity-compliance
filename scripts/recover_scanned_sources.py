"""Recover scanned source text locally while retaining every page image and OCR box."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import sys

from collect_source_originals import now, read_jsonl, save_object


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--ocr-packages', type=Path, required=True)
    parser.add_argument('--limit', type=int, default=1000)
    args = parser.parse_args()
    sys.path.insert(0, str(args.ocr_packages.resolve()))
    import pypdfium2 as pdfium
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
    engine = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=1, det_limit_side_len=1280, rec_batch_num=12)
    root = args.root.resolve()
    targets = json.loads((root / 'data/source-recovery-targets.json').read_text(encoding='utf-8'))['targets']
    log = root / 'source-originals/recovery-ocr.jsonl'
    completed = {r['canonical_url'] for r in read_jsonl(log)}
    queue = [r for r in targets if r['route'] == 'pdf-ocr' and r['canonical_url'] not in completed][:args.limit]
    print(json.dumps({'queued_scanned_documents': len(queue)}), flush=True)
    with log.open('a', encoding='utf-8', newline='\n') as handle:
        for target in queue:
            prior = target['prior']
            try:
                raw = (root / prior['snapshot_path']).read_bytes()
                if hashlib.sha256(raw).hexdigest() != prior['sha256']:
                    raise ValueError('Original PDF hash mismatch')
                document = pdfium.PdfDocument(raw)
                units, images, missing, confidence = [], [], [], []
                try:
                    for index in range(len(document)):
                        page = document[index]
                        bitmap = page.render(scale=3.0)
                        pil = bitmap.to_pil().convert('RGB')
                        buffer = io.BytesIO()
                        pil.save(buffer, format='PNG')
                        image_path, image_hash = save_object(root, buffer.getvalue(), '.png')
                        textpage = page.get_textpage()
                        native = textpage.get_text_range().strip()
                        textpage.close()
                        boxes = []
                        method = 'pdfium-native-text'
                        if len(native) >= 80:
                            text = native
                        else:
                            result, _ = engine(np.asarray(pil))
                            method = 'rapidocr-onnxruntime-1.4.4'
                            boxes = [{'box': box, 'text': text, 'confidence': float(score)} for box, text, score in (result or [])]
                            text = '\n'.join(row['text'] for row in boxes)
                            confidence.extend(row['confidence'] for row in boxes)
                        if text.strip():
                            units.append({'locator': f'page:{index + 1}', 'text': text})
                        else:
                            missing.append(index + 1)
                        images.append({'page': index + 1, 'image_path': image_path, 'image_sha256': image_hash,
                                       'width': pil.width, 'height': pil.height, 'method': method, 'ocr_boxes': boxes})
                        bitmap.close()
                        page.close()
                        print(json.dumps({'url': target['canonical_url'], 'page': index + 1, 'characters': len(text), 'method': method}), flush=True)
                    count = len(document)
                finally:
                    document.close()
                if not units:
                    raise ValueError('No source text recovered on any page')
                text_path, text_hash = save_object(root, (json.dumps(units, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
                ocr_path, ocr_hash = save_object(root, (json.dumps(images, ensure_ascii=True, indent=2) + '\n').encode(), '.json')
                row = {**prior, 'recovery_status': 'captured', 'extraction_refreshed_at': now(),
                       'extraction_status': 'ocr-extracted-unreviewed', 'text_path': text_path, 'text_sha256': text_hash,
                       'text_character_count': sum(len(unit['text']) for unit in units), 'page_count': count,
                       'pages_without_text': missing, 'ocr_pages_path': ocr_path, 'ocr_pages_sha256': ocr_hash,
                       'ocr_review_status': 'needs-visual-and-critical-field-review',
                       'ocr_mean_line_confidence': sum(confidence) / len(confidence) if confidence else None,
                       'legal_review_status': 'not-reviewed', 'current_law_release': False}
            except Exception as exc:
                row = {'canonical_url': target['canonical_url'], 'recovery_status': 'failed', 'reason': f'{type(exc).__name__}: {exc}', 'attempted_at': now()}
            handle.write(json.dumps(row, ensure_ascii=True) + '\n')
            handle.flush()
            print(json.dumps({'completed': target['canonical_url'], 'status': row['recovery_status'], 'reason': row.get('reason')}), flush=True)


if __name__ == '__main__':
    main()
