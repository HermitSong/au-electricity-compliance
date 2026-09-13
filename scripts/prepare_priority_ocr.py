"""Prepare, bound and report local OCR using isolated copies of the existing engines."""
import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import runpy
import subprocess
import sys
import time
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
from collect_source_originals import read_jsonl, save_object
from merge_source_recovery import fingerprint
from recover_preserved_pdf_text import contained_path, verified_original, substantive_count
from validate_source_originals import check_artifacts

STAGE = Path(__file__).resolve().parents[1]
ROOT = STAGE / "ocr-recovery"
OFFLINE = STAGE / "offline-recovery"
PACKAGES = STAGE.parent / "au-power-recovery-tools/python"
TESSDATA = STAGE.parent / "au-power-recovery-tools/tessdata"
ENGINES = ("recover_scanned_sources.py", "double_extract_scanned_sources.py")


def dump(path, value):
    path = contained_path(ROOT, path)
    data = (json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n").encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists() or path.read_bytes() != data:
        path.write_bytes(data)


def priority(row):
    text = unquote(json.dumps([row.get(k) for k in ("canonical_url", "link_label", "discovered_from", "source_family_ids")])).lower()
    host = (urlparse(row["canonical_url"]).hostname or "").lower()
    if not host.endswith(".gov.au"):
        return None, "not-official-government-host"
    if re.search(r"submiss|policy|fact.sheet|practice.note|review.redacted", text):
        return None, "submission-policy-or-guidance"
    if re.search(r"clearing|vegetation|vcn.cps|environmental-enforcement|wa-dwer", text):
        return None, "broad-non-electricity-environmental-register"
    if re.search(r"eipn\(g\)|pn\(g\)|sumo-gas", text):
        return None, "gas-specific-deferred-for-electricity-priority"
    if not re.search(r"penalt|infring|undertak|judgm?ent|prosecut", text):
        return None, "no-priority-enforcement-document-context"
    if "electricity" not in text and not (host == "www.esc.vic.gov.au" and "vic-esc-penalties" in text):
        return None, "electricity-relevance-not-established-by-metadata"
    return 0, "official-electricity-or-retailer-enforcement-attachment; document identity unreviewed"


def select(rows, max_docs=30, max_pages=100):
    if not 0 < max_docs <= 30 or not 0 < max_pages <= 100:
        raise ValueError("Hard bounds are 30 documents and 100 pages")
    eligible, excluded, seen = [], [], set()
    for row in rows:
        key = (row["canonical_url"], row["sha256"])
        if key in seen:
            continue
        seen.add(key)
        rank, reason = priority(row)
        if row.get("recovery_status") != "failed":
            rank, reason = None, "not-still-missing"
        if type(row.get("page_count")) is not int or row["page_count"] <= 0:
            rank, reason = None, "unknown-page-count"
        if rank is None:
            excluded.append({"canonical_url": row["canonical_url"], "reason": reason})
        else:
            eligible.append((rank, row["page_count"], row["canonical_url"], row, reason))
    chosen, pages = [], 0
    for _, count, url, row, reason in sorted(eligible):
        if len(chosen) >= max_docs or pages + count > max_pages:
            excluded.append({"canonical_url": url, "reason": "document-or-page-budget", "pages": count})
            continue
        chosen.append((row, reason))
        pages += count
    return chosen, excluded


def prepare(max_docs=30, max_pages=100):
    if ROOT.resolve() != ROOT or not ROOT.resolve().is_relative_to(STAGE.resolve()):
        raise ValueError("OCR output root must not redirect outside the stage")
    failure_path = OFFLINE / "pdfium-native-failures.jsonl"
    failures = read_jsonl(failure_path)
    chosen, excluded = select(failures, max_docs, max_pages)
    targets = []
    import pypdfium2 as pdfium
    for row, reason in chosen:
        data, suffix = verified_original(OFFLINE, row)
        with pdfium.PdfDocument(data) as doc:
            if len(doc) != row["page_count"]:
                raise ValueError("Preserved page count changed")
        prior = dict(row["preserved_source_provenance"]["source_record"])
        path, digest = save_object(ROOT, data, suffix)
        prior.update(snapshot_path=path, sha256=digest, legal_review_status="not-reviewed",
                     current_law_release=False, redistribution_status="not-cleared",
                     offline_ocr_provenance={"input_root": str(OFFLINE), "input_snapshot_path": row["snapshot_path"],
                                             "original_sha256": digest, "original_copied_not_moved": True,
                                             "new_download": False, "network_used": False,
                                             "prior_native_failure_fingerprint": row["recovery_fingerprint"]})
        targets.append({"canonical_url": prior["canonical_url"], "route": "pdf-ocr", "prior": prior,
                        "page_count": row["page_count"], "selection_reason": reason})
    report = {"targets": targets, "selected_documents": len(targets),
              "selected_pages": sum(row["page_count"] for row in targets), "input_missing_pdfs": len(failures),
              "max_documents": max_docs, "max_pages": max_pages, "excluded": excluded,
              "input_failures_sha256": hashlib.sha256(failure_path.read_bytes()).hexdigest(),
              "legal_review_status": "not-reviewed", "current_law_release": False,
              "visual_review_status": "not-performed"}
    dump("data/source-recovery-targets.json", report)
    return report


def guard_engine():
    allowed = ROOT.resolve()
    def guard(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto", "socket.sendmsg"}:
            raise PermissionError("Network disabled for offline OCR")
        paths = []
        if event == "open" and isinstance(args[0], (str, bytes)):
            mode, flags = args[1], args[2]
            if (isinstance(mode, str) and any(c in mode for c in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                paths = [args[0]]
        elif event in {"os.mkdir", "os.remove", "os.rmdir"}:
            paths = [args[0]]
        elif event in {"os.rename", "os.link", "os.symlink"}:
            paths = list(args[:2])
        for value in paths:
            if not Path(os.fsdecode(value)).resolve().is_relative_to(allowed):
                raise PermissionError("OCR writes restricted to stage/ocr-recovery")
    sys.addaudithook(guard)


def engine(which):
    guard_engine()
    script = ROOT / "scripts" / ENGINES[which]
    sys.path.insert(0, str(PACKAGES))
    sys.argv = [str(script), "--root", str(ROOT), "--ocr-packages", str(PACKAGES)]
    sys.argv += ["--limit", "30"] if which == 0 else ["--tessdata", str(TESSDATA)]
    runpy.run_path(str(script), run_name="__main__")


def run_batch(seconds):
    if not 0 < seconds <= 600:
        raise ValueError("OCR execution budget must be at most 600 seconds")
    previous = ROOT / "execution.json"
    phases = json.loads(previous.read_bytes())["phases"] if previous.exists() else []
    spent = sum(phase["elapsed_seconds"] for phase in phases)
    seconds = min(seconds, max(0, 600 - spent))
    started = time.monotonic()
    (ROOT / "logs").mkdir(parents=True, exist_ok=True)
    (ROOT / "tmp").mkdir(parents=True, exist_ok=True)
    for which in range(2):
        left = seconds - (time.monotonic() - started)
        allowance = min(left, seconds * 0.65) if which == 0 else left
        if allowance <= 0:
            break
        command = [sys.executable, "-B", str(Path(__file__).resolve()), "engine-first" if which == 0 else "engine-second"]
        begin = time.monotonic()
        phase = {"engine": ENGINES[which], "budget_seconds": allowance}
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TEMP=str(ROOT / "tmp"), TMP=str(ROOT / "tmp"), OMP_THREAD_LIMIT="2")
        with (ROOT / "logs" / (ENGINES[which] + ".log")).open("ab") as log:
            try:
                process = subprocess.run(command, cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=allowance)
                phase.update(status="completed" if process.returncode == 0 else "failed", returncode=process.returncode)
            except subprocess.TimeoutExpired:
                phase.update(status="time-budget-exhausted", interrupted_document_outputs="not accepted without complete log row")
        phase["elapsed_seconds"] = round(time.monotonic() - begin, 3)
        phases.append(phase)
        dump("execution.json", {"budget_seconds": 600, "this_invocation_budget_seconds": seconds,
                                "phases": phases, "elapsed_seconds": round(spent + time.monotonic() - started, 3)})
        print(json.dumps(phase), flush=True)
    return phases


def low_confidence_words(tsv, threshold=85):
    fields = "level page_num block_num par_num line_num word_num left top width height conf text".split()
    rows = csv.DictReader(io.StringIO(tsv), delimiter="\t", fieldnames=fields)
    result = []
    for word in rows:
        if word.get("level") == "level":
            continue
        if word.get("text", "").strip() and 0 <= float(word["conf"]) < threshold:
            result.append(word)
    return result


def quality_report():
    targets = json.loads((ROOT / "data/source-recovery-targets.json").read_bytes())
    first = {r["canonical_url"]: r for r in read_jsonl(ROOT / "source-originals/recovery-ocr.jsonl")}
    second = {r["canonical_url"]: r for r in read_jsonl(ROOT / "source-originals/recovery-ocr-double.jsonl")}
    documents, candidates, checked, errors = [], [], set(), []
    for target in targets["targets"]:
        url = target["canonical_url"]
        a, b = first.get(url), second.get(url)
        record = {"canonical_url": url, "pages_expected": target["page_count"], "first_engine_status": (a or {}).get("recovery_status", "not-completed"),
                  "second_engine_status": "completed" if b else "not-completed", "pages": [],
                  "visual_review_status": "not-performed", "legal_review_status": "not-reviewed", "current_law_release": False}
        if a and a.get("recovery_status") == "captured":
            check_artifacts(ROOT, a, checked, errors)
            pages = json.loads((ROOT / a["ocr_pages_path"]).read_bytes())
            comparison = {}
            if b:
                check_artifacts(ROOT, b, checked, errors)
                comparison = {p["page"]: p for p in json.loads((ROOT / b["ocr_comparison_path"]).read_bytes())}
            for page in pages:
                comp = comparison.get(page["page"], {})
                low_lines = [box for box in page["ocr_boxes"] if box["confidence"] < 0.90]
                low_words = []
                if comp:
                    tsv = (ROOT / comp["tesseract_word_boxes_path"]).read_text(encoding="utf-8")
                    low_words = low_confidence_words(tsv)
                record["pages"].append({"locator": f"page:{page['page']}", "image_path": page["image_path"],
                                        "first_engine_method": page["method"], "rapidocr_low_confidence_lines": low_lines,
                                        "tesseract_low_confidence_words": low_words, "tesseract_mean_confidence": comp.get("tesseract_mean_confidence"),
                                        "second_engine_completed": bool(comp), "tesseract_empty": comp.get("tesseract_empty"),
                                        "text_selected_from": comp.get("text_selected_from"),
                                        "alphanumeric_similarity": comp.get("alphanumeric_similarity"),
                                        "tokens_only_in_first": comp.get("tokens_only_in_first", []),
                                        "tokens_only_in_second": comp.get("tokens_only_in_second", []),
                                        "critical_token_disagreement": bool(comp.get("tokens_only_in_first") or comp.get("tokens_only_in_second")),
                                        "critical_tokens_on_low_confidence_first_lines": [box for box in low_lines if re.search(r"\d", box["text"])],
                                        "critical_tokens_on_low_confidence_second_words": [word for word in low_words if re.search(r"\d", word["text"])]})
            chosen = dict(b or a)
            units = json.loads((ROOT / chosen["text_path"]).read_bytes())
            if sum(substantive_count(u["text"]) for u in units) >= 80 and all(u["text"].strip() for u in units):
                chosen.update(extraction_completeness="incomplete" if chosen["pages_without_text"] else "completeness-unreviewed",
                              visual_review_status="not-performed", legal_review_status="not-reviewed", current_law_release=False,
                              review_status="research-only; not legal clearance", numeric_disagreement_review="not-performed")
                chosen["recovery_fingerprint"] = fingerprint(chosen)
                candidates.append(chosen)
            record["all_page_image_evidence"] = [p["page"] for p in pages] == list(range(1, target["page_count"] + 1))
        documents.append(record)
    page_rows = [p for d in documents for p in d["pages"]]
    report = {"selected_documents": targets["selected_documents"], "selected_pages": targets["selected_pages"],
              "first_engine_completed_documents": sum(d["first_engine_status"] == "captured" for d in documents),
              "second_engine_completed_documents": len(second), "candidate_recovered_documents": len(candidates),
              "recovered_text_pages": sum(len(json.loads((ROOT / r["text_path"]).read_bytes())) for r in candidates),
              "page_image_evidence_pages": len(page_rows), "dual_engine_comparison_pages": sum(p["second_engine_completed"] for p in page_rows),
              "critical_token_disagreement_pages": sum(p["critical_token_disagreement"] for p in page_rows),
              "low_confidence_pages": sum(bool(p["rapidocr_low_confidence_lines"] or p["tesseract_low_confidence_words"]) for p in page_rows),
              "rapidocr_low_confidence_lines": sum(len(p["rapidocr_low_confidence_lines"]) for p in page_rows),
              "tesseract_low_confidence_words": sum(len(p["tesseract_low_confidence_words"]) for p in page_rows),
              "tesseract_empty_pages": sum(p["tesseract_empty"] is True for p in page_rows),
              "integrity_objects_checked": len(checked), "integrity_errors": errors,
              "thresholds": {"rapidocr_line_below": 0.90, "tesseract_word_below": 85},
              "network_used": False, "visual_review_status": "not-performed", "legal_review_status": "not-reviewed",
              "current_law_release": False, "merged": False,
              "limitations": ["Confidence values are engine scores, not calibrated correctness probabilities.",
                              "Numeric token differences include dates, amounts, identifiers and OCR formatting differences; none are adjudicated.",
                              "Both engines can share errors; agreement does not prove accuracy or completeness.",
                              "All pages are required for a completed document; interrupted document objects are not merge candidates."],
              "documents": documents}
    if errors:
        candidates = []
        report["candidate_recovered_documents"] = 0
    dump("quality-report.json", report)
    path = ROOT / "source-originals/recovery-priority-ocr.jsonl"
    path.write_text("".join(json.dumps(r, ensure_ascii=True, sort_keys=True) + "\n" for r in candidates), encoding="utf-8")
    return {k: v for k, v in report.items() if k != "documents"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "run", "report", "engine-first", "engine-second"])
    parser.add_argument("--max-docs", type=int, default=30)
    parser.add_argument("--max-pages", type=int, default=100)
    parser.add_argument("--seconds", type=int, default=420)
    args = parser.parse_args()
    if args.mode.startswith("engine-"):
        engine(0 if args.mode == "engine-first" else 1)
    elif args.mode == "prepare":
        result = prepare(args.max_docs, args.max_pages)
        print(json.dumps({k: v for k, v in result.items() if k not in {"targets", "excluded"}}, indent=2))
    elif args.mode == "run":
        run_batch(args.seconds)
        print(json.dumps(quality_report(), indent=2))
    else:
        print(json.dumps(quality_report(), indent=2))


if __name__ == "__main__":
    main()
