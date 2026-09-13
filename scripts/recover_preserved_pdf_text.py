"""Offline native PDFium recovery of missing-text preserved originals. No OCR."""

from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sys

# Importing archive helpers must never create bytecode in the canonical archive.
sys.dont_write_bytecode = True
from collect_source_originals import normalise_url, now, read_jsonl, save_object
from merge_source_recovery import fingerprint, is_fallback


OUTPUT_BASE = Path(__file__).resolve().parents[1] / "offline-recovery"
MIN_SUBSTANTIVE_CHARS = 80
METHOD = "pdfium-native-text"
REVISION = 1
SUCCESS_LOG = "source-originals/recovery-pdfium-native.jsonl"
FAILURE_LOG = "pdfium-native-failures.jsonl"
SUMMARY = "pdfium-native-summary.json"
URL_SUMMARY = "pdfium-native-urls.jsonl"
BOUNDARY = "research-only; not legal clearance"


class RecoveryError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8")


def contained_path(root, relative, objects=False):
    relative = str(relative)
    parts = relative.replace("\\", "/").split("/")
    if (not relative or PureWindowsPath(relative).drive or Path(relative).is_absolute()
            or ".." in parts):
        raise RecoveryError("path-containment", "Relative path escapes its permitted root")
    root = Path(root).resolve()
    base = root / "source-originals" / "objects" if objects else root
    path = (root / relative).resolve()
    if not base.resolve().is_relative_to(root) or not path.is_relative_to(base.resolve()):
        raise RecoveryError("path-containment", "Resolved path escapes its permitted root")
    return path


def validate_output_root(source_root, output_root):
    source_root, output_root = Path(source_root).resolve(), Path(output_root).resolve()
    # Reject an offline-recovery symlink/junction escaping the stage as well.
    base = OUTPUT_BASE.resolve()
    if (not base.is_relative_to(OUTPUT_BASE.parent.resolve()) or not output_root.is_relative_to(base)
            or output_root.is_relative_to(source_root) or source_root.is_relative_to(output_root)):
        raise RecoveryError("output-containment", "Output must be inside stage/offline-recovery and disjoint from the source archive")
    return source_root, output_root


def verified_original(source_root, prior):
    path = contained_path(source_root, prior.get("snapshot_path", ""), objects=True)
    digest = prior.get("sha256", "")
    if not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise RecoveryError("invalid-original-hash", "Original requires a lowercase SHA-256 digest")
    data = path.read_bytes()
    if sha256(data) != digest:
        raise RecoveryError("original-hash-mismatch", "Original PDF hash mismatch")
    expected = Path("source-originals") / "objects" / digest[:2] / (digest + path.suffix)
    if path != contained_path(source_root, expected, objects=True):
        raise RecoveryError("original-hashpath-mismatch", "Original path is not its content-addressed hashpath")
    return data, path.suffix


def preserve(output_root, data, suffix):
    digest = sha256(data)
    relative = Path("source-originals") / "objects" / digest[:2] / (digest + suffix)
    contained_path(output_root, relative, objects=True)
    return save_object(output_root, data, suffix)


def substantive_count(text):
    """Count letters/digits, excluding whitespace, punctuation and control glyphs."""
    return sum(character.isalnum() for character in text)


def extract_native(data, pdfium):
    result = {"units": [], "page_count": None, "pages_attempted": 0,
              "pages_without_text": [], "page_errors": [], "encrypted": None,
              "all_pages_attempted": False, "native_text_all_pages_present": False}
    try:
        with closing(pdfium.PdfDocument(data)) as document:
            result["page_count"] = len(document)
            revision = pdfium.raw.FPDF_GetSecurityHandlerRevision(document)
            result["encrypted"] = revision != -1
            if result["encrypted"]:
                raise RecoveryError("encrypted-pdf", "Encrypted PDF deferred; no password supplied or attempted")
            for index in range(len(document)):
                number = index + 1
                result["pages_attempted"] += 1
                try:
                    with closing(document[index]) as page, closing(page.get_textpage()) as textpage:
                        text = textpage.get_text_range(errors="strict").replace("\r\n", "\n")
                        text = "".join(c for c in text if c.isprintable() or c in "\n\t").strip()
                    if substantive_count(text):
                        result["units"].append({"locator": f"page:{number}", "text": text})
                    else:
                        result["pages_without_text"].append(number)
                except Exception as exc:
                    result["pages_without_text"].append(number)
                    result["page_errors"].append({"locator": f"page:{number}", "page": number,
                                                  "error": f"{type(exc).__name__}: {exc}"})
            result["all_pages_attempted"] = True
            result["native_text_all_pages_present"] = bool(len(document)) and not result["pages_without_text"]
    except Exception as exc:
        code = getattr(exc, "code", "unreadable-pdf")
        if getattr(exc, "err_code", None) == pdfium.raw.FPDF_ERR_PASSWORD:
            code, result["encrypted"] = "encrypted-pdf", True
        result.update(reason_code=code, reason=f"{type(exc).__name__}: {exc}")
    return result


def recover_one(source_root, output_root, prior, pdfium, provenance):
    source_root, output_root = validate_output_root(source_root, output_root)
    row = deepcopy(prior)
    for key in ("text_path", "text_sha256", "text_character_count", "extraction_error",
                "extraction_refreshed_at", "recovery_import_id", "recovery_imported_at"):
        row.pop(key, None)
    row.update(extraction_method=METHOD, extraction_revision=REVISION,
               extraction_status="extraction-error", extraction_completeness="incomplete",
               recovery_status="failed", legal_review_status="not-reviewed", current_law_release=False,
               redistribution_status="not-cleared", review_status=BOUNDARY,
               text_character_count=0, substantive_character_count=0, page_count=None,
               pages_attempted=0, pages_without_text=[], page_errors=[], all_pages_attempted=False,
               native_text_all_pages_present=False, original_hash_validated=False,
               original_bytes_unchanged=False, original_copied=False,
               preserved_source_provenance={**provenance, "source_record": deepcopy(prior)},
               extractor_provenance={"method": METHOD, "revision": REVISION,
                                     "pypdfium2_version": str(pdfium.PYPDFIUM_INFO),
                                     "pdfium_version": str(pdfium.PDFIUM_INFO),
                                     "api": "PdfTextPage.get_text_range(errors='strict')",
                                     "input": "previously-preserved-original-bytes",
                                     "new_download": False, "network_used": False, "ocr_used": False,
                                     "password_attempted": False,
                                     "minimum_substantive_characters": MIN_SUBSTANTIVE_CHARS,
                                     "substantive_character_definition": "Unicode letters and digits (str.isalnum)"})
    try:
        data, suffix = verified_original(source_root, prior)
        row["original_hash_validated"] = True
        if b"%PDF-" not in data[:1024]:
            raise RecoveryError("not-pdf-bytes", "Preserved bytes do not contain a PDF header")
    except (OSError, ValueError) as exc:
        row.update(reason_code=getattr(exc, "code", "unreadable-original"), reason=f"{type(exc).__name__}: {exc}")
        return row

    # save_object verifies existing copies and never moves or rewrites the source.
    snapshot, digest = preserve(output_root, data, suffix)
    row.update(snapshot_path=snapshot, sha256=digest, original_copied=True)
    extracted = extract_native(data, pdfium)
    units = extracted.pop("units")
    row.update(extracted)
    after, _ = verified_original(source_root, prior)
    row["original_bytes_unchanged"] = after == data
    if not row["original_bytes_unchanged"]:
        raise RecoveryError("source-changed-during-recovery", "Source original changed during extraction")
    row["text_character_count"] = sum(len(unit["text"]) for unit in units)
    row["substantive_character_count"] = sum(substantive_count(unit["text"]) for unit in units)
    if row.get("reason_code"):
        return row
    usable = row["substantive_character_count"] >= MIN_SUBSTANTIVE_CHARS
    if not usable:
        row.update(reason_code="page-extraction-error" if row["page_errors"] else "insufficient-native-text",
                   reason="Native text below 80 substantive characters across the document",
                   extraction_status="extraction-error" if row["page_errors"] else "needs-ocr-or-blank-page-review")
        return row
    text_path, text_digest = preserve(output_root, encoded(units), ".json")
    incomplete = bool(row["pages_without_text"] or row["page_errors"])
    row.update(recovery_status="captured", content_class="pdf-document", text_path=text_path,
               text_sha256=text_digest, extraction_status="needs-ocr-or-blank-page-review" if incomplete else "extracted-unreviewed",
               extraction_completeness="incomplete" if incomplete else "completeness-unreviewed",
               recovered_page_count=len(units))
    return row


def targets_from_report(source_root, manifest_rows, report):
    missing = {normalise_url(row["canonical_url"]): row for row in report["urls"]
               if row["has_research_text"] is False}
    originals = {}
    for number, row in enumerate(manifest_rows, 1):
        url = normalise_url(row["canonical_url"])
        if url in missing and row.get("snapshot_path") and not is_fallback(row):
            originals[url] = (number, row)
    targets, excluded = [], []
    for url, report_row in sorted(missing.items()):
        saved = originals.get(url)
        if not saved:
            excluded.append({"canonical_url": url, "recovery_status": "out-of-scope",
                             "reason_code": "no-preserved-original", "prior_extraction_status": report_row.get("extraction_status")})
            continue
        number, row = saved
        hint = ("pdf" in row.get("content_type", "").lower()
                or str(row["snapshot_path"]).lower().endswith(".pdf"))
        if not hint:
            try:
                with contained_path(source_root, row["snapshot_path"], objects=True).open("rb") as handle:
                    hint = b"%PDF-" in handle.read(1024)
            except (OSError, ValueError):
                # Include inaccessible preserved objects so the failure is visible.
                hint = True
        if hint:
            targets.append((number, row))
        else:
            excluded.append({"canonical_url": url, "recovery_status": "out-of-scope",
                             "reason_code": "preserved-non-pdf", "prior_extraction_status": row.get("extraction_status")})
    return targets, excluded


def log_identity(row):
    if row["recovery_status"] == "captured":
        return fingerprint(row)
    return sha256(encoded({"merge_fingerprint": fingerprint(row), "reason_code": row.get("reason_code"),
                          "source_record": row["preserved_source_provenance"]["source_record"],
                          "extractor_provenance": row["extractor_provenance"]}))


def append_result(output_root, row, existing):
    identity = log_identity(row)
    if identity in existing:
        return existing[identity], False
    row.update(recovery_fingerprint=identity, extraction_refreshed_at=now())
    relative = SUCCESS_LOG if row["recovery_status"] == "captured" else FAILURE_LOG
    path = contained_path(output_root, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")
    existing[identity] = row
    return row, True


def write_changed(output_root, relative, data):
    path = contained_path(output_root, relative)
    if path.exists() and path.read_bytes() == data:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def run(source_root, output_root, readiness_report=None, pdfium=None, progress=None):
    source_root, output_root = validate_output_root(source_root, output_root)
    manifest_path = contained_path(source_root, "source-originals/manifest.jsonl")
    report_path = (Path(readiness_report) if readiness_report else
                   contained_path(source_root, "review/results/delivery-readiness.json"))
    manifest_bytes, report_bytes = manifest_path.read_bytes(), report_path.read_bytes()
    manifest_hash, report_hash = sha256(manifest_bytes), sha256(report_bytes)
    report = json.loads(report_bytes)
    recorded = [row["sha256"] for row in report["inputs"]
                if row.get("role") == "archive" and row.get("path") == "source-originals/manifest.jsonl"]
    if recorded != [manifest_hash] or not report.get("archive_available"):
        raise RecoveryError("stale-readiness-report", "Readiness report must identify this exact source manifest")
    manifest_rows = [json.loads(line) for line in manifest_bytes.decode("utf-8-sig").splitlines() if line.strip()]
    targets, excluded = targets_from_report(source_root, manifest_rows, report)
    if pdfium is None:
        import pypdfium2 as pdfium
    existing = {}
    for relative in (SUCCESS_LOG, FAILURE_LOG):
        for row in read_jsonl(contained_path(output_root, relative)):
            identity = log_identity(row)
            if row.get("recovery_fingerprint") != identity or identity in existing:
                raise RecoveryError("invalid-recovery-log", "Recovery log fingerprint mismatch or duplicate")
            existing[identity] = row
    outcomes, appended = [], Counter()
    for index, (line, prior) in enumerate(targets, 1):
        provenance = {"archive_root": str(source_root), "manifest_path": "source-originals/manifest.jsonl",
                      "manifest_sha256": manifest_hash, "manifest_record_number": line,
                      "source_record_sha256": sha256(encoded(prior)), "readiness_report_sha256": report_hash}
        row = recover_one(source_root, output_root, prior, pdfium, provenance)
        row, added = append_result(output_root, row, existing)
        appended[row["recovery_status"]] += added
        outcomes.append(row)
        if progress:
            progress({"completed": index, "total": len(targets), "canonical_url": row["canonical_url"],
                      "status": row["recovery_status"], "pages": row["page_count"],
                      "text_pages": row.get("recovered_page_count", 0), "reason": row.get("reason_code")})
    if manifest_path.read_bytes() != manifest_bytes or report_path.read_bytes() != report_bytes:
        raise RecoveryError("source-inputs-changed", "Source manifest or readiness report changed during recovery")
    successes = [row for row in outcomes if row["recovery_status"] == "captured"]
    failures = [row for row in outcomes if row["recovery_status"] == "failed"]
    counts = {"missing_text_urls_before": len(targets) + len(excluded), "candidate_pdf_urls": len(targets),
              "distinct_candidate_pdf_hashes": len({row.get("sha256") for _, row in targets}),
              "recovered_text_urls": len(successes), "failed_pdf_urls": len(failures),
              "out_of_scope_urls": len(excluded),
              "remaining_missing_text_urls_if_merged": len(failures) + len(excluded),
              "recovered_all_pages_with_native_text": sum(row["native_text_all_pages_present"] for row in successes),
              "recovered_incomplete_documents": sum(row["extraction_completeness"] == "incomplete" for row in successes),
              "pdf_pages_total_known": sum(row["page_count"] or 0 for row in outcomes),
              "pdf_pages_attempted": sum(row["pages_attempted"] for row in outcomes),
              "documents_all_pages_attempted": sum(row["all_pages_attempted"] for row in outcomes),
              "documents_unknown_page_count": sum(row["page_count"] is None for row in outcomes),
              "recovered_text_pages": sum(row.get("recovered_page_count", 0) for row in successes),
              "pages_without_native_text": sum(len(row["pages_without_text"]) for row in outcomes),
              "page_extraction_errors": sum(len(row["page_errors"]) for row in outcomes),
              "recovered_substantive_characters": sum(row["substantive_character_count"] for row in successes),
              "original_hashes_validated": sum(row["original_hash_validated"] for row in outcomes),
              "original_copies_verified": sum(row["original_copied"] for row in outcomes),
              "originals_unchanged_verified": sum(row["original_bytes_unchanged"] for row in outcomes)}
    report_out = {"schema_version": "1.0", "recovery_kind": "offline-preserved-pdf-native-text",
                  "archive_root": str(source_root), "output_root": str(output_root),
                  "manifest_sha256": manifest_hash, "readiness_report_sha256": report_hash,
                  "source_manifest_and_report_unchanged": True, "network_used": False, "ocr_used": False,
                  "canonical_archive_modified": False, "merged_into_canonical_archive": False,
                  "legal_review_status": "not-reviewed", "current_law_release": False,
                  "review_status": BOUNDARY, "counts": counts,
                  "candidate_prior_extraction_status_counts": dict(Counter(row.get("extraction_status") for _, row in targets)),
                  "failure_reason_counts": dict(Counter(row["reason_code"] for row in failures)),
                  "excluded_reason_counts": dict(Counter(row["reason_code"] for row in excluded)),
                  "success_log": SUCCESS_LOG, "failure_log": FAILURE_LOG, "url_summary": URL_SUMMARY,
                  "limitations": ["Native text availability does not prove extraction or visual completeness.",
                                  "Blank and failed pages remain unresolved; OCR was not attempted.",
                                  "Recovery retains the original acquisition time and source metadata; it is not a new download.",
                                  "No source acquisition, temporal case reconciliation or legal approval is performed.",
                                  "Parent must explicitly merge the success log and copied objects; existing merge LOGS are unchanged."]}
    url_rows = list(excluded)
    fields = ("canonical_url", "response_url", "source_family_ids", "recovery_status", "reason_code", "reason",
              "recovery_fingerprint", "snapshot_path", "sha256", "text_path", "text_sha256", "page_count",
              "pages_attempted", "recovered_page_count", "pages_without_text", "page_errors", "encrypted",
              "substantive_character_count", "extraction_status", "extraction_completeness",
              "legal_review_status", "current_law_release")
    for row in outcomes:
        url_rows.append({**{key: row[key] for key in fields if key in row},
                         "prior_extraction_status": row["preserved_source_provenance"]["source_record"].get("extraction_status")})
    write_changed(output_root, URL_SUMMARY, "".join(json.dumps(row, sort_keys=True) + "\n"
                                                   for row in sorted(url_rows, key=lambda row: row["canonical_url"])).encode("utf-8"))
    write_changed(output_root, SUMMARY, encoded(report_out))
    return {**report_out, "success_rows_appended_this_run": appended["captured"],
            "failure_rows_appended_this_run": appended["failed"]}


def deny_network(event, args):
    if event in {"socket.connect", "socket.getaddrinfo", "socket.gethostbyname", "socket.sendto", "socket.sendmsg"}:
        raise RuntimeError("Network is disabled for preserved-PDF recovery")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, default=OUTPUT_BASE)
    parser.add_argument("--readiness-report", type=Path)
    parser.add_argument("--pdfium-packages", type=Path, help="Optional existing local package directory; never installs packages")
    args = parser.parse_args()
    sys.addaudithook(deny_network)
    if args.pdfium_packages:
        sys.path.insert(0, str(args.pdfium_packages.resolve()))
    report = run(args.source_root, args.output_root, args.readiness_report,
                 progress=lambda row: print(json.dumps(row), flush=True))
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
