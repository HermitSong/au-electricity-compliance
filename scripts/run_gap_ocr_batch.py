"""Bounded, offline dual OCR of the current missing-text cohort; canonical read-only."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from copy import deepcopy
from difflib import SequenceMatcher
import hashlib
import io
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from urllib.parse import unquote, urlparse

sys.dont_write_bytecode = True
from collect_source_originals import now, read_jsonl, save_object, select_manifest_rows
from double_extract_scanned_sources import critical_tokens
from merge_source_recovery import fingerprint, is_fallback
from prepare_priority_ocr import low_confidence_words
from recover_preserved_pdf_text import contained_path, encoded, substantive_count, verified_original
from validate_source_originals import check_artifacts

STAGE = Path(__file__).resolve().parents[1]
ROOT = STAGE / "ocr-gap-recovery"
SOURCE = STAGE
PACKAGES = STAGE.parent / "au-power-recovery-tools/python"
TESSDATA = PACKAGES.parent / "tessdata"
REPORT = STAGE / "review/results/ocr-gap-recovery-2026-09-07.json"
FINAL_LOG = "source-originals/recovery-priority-ocr.jsonl"
MAX_DOCS, MAX_PAGES, MAX_SECONDS = 40, 240, 1200
BOUNDARY = {"legal_review_status": "not-reviewed", "current_law_release": False,
            "redistribution_status": "not-cleared", "review_status": "research-only; not legal clearance"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(relative, value):
    path = contained_path(ROOT, relative)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(encoded(value))
    for attempt in range(5):
        try:
            os.replace(temporary, path)
            break
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.025 * (2 ** attempt))


def object_json(value):
    return save_object(ROOT, encoded(value), ".json")


def guard_writes():
    allowed = ROOT.resolve()
    if allowed.is_relative_to(SOURCE.resolve()) or SOURCE.resolve().is_relative_to(allowed):
        raise ValueError("OCR output must be disjoint from the canonical SOURCE archive, including when this runner is installed there")
    if allowed != ROOT or not allowed.is_relative_to(STAGE.resolve()):
        raise ValueError("Output root redirects outside assigned stage")
    if REPORT.resolve() != REPORT or REPORT.with_suffix(".md").resolve() != REPORT.with_suffix(".md"):
        raise ValueError("Report paths must not redirect outside assigned files")
    report_paths = {REPORT.resolve(), REPORT.with_suffix(".md").resolve()}

    def guard(event, args):
        if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto", "socket.sendmsg"}:
            raise PermissionError("Offline OCR cannot use the network")
        paths = []
        if event == "open" and isinstance(args[0], (str, bytes)):
            mode, flags = args[1], args[2]
            if (isinstance(mode, str) and any(c in mode for c in "wax+")) or (flags or 0) & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC):
                paths = [args[0]]
        elif event in {"os.mkdir", "os.remove", "os.rmdir", "os.chmod", "os.utime"}:
            paths = [args[0]]
        elif event in {"os.rename", "os.link", "os.symlink"}:
            paths = list(args[:2])
        for value in paths:
            path = Path(os.fsdecode(value)).resolve()
            if not path.is_relative_to(allowed) and path not in report_paths:
                raise PermissionError("Write outside assigned OCR outputs: " + str(path))
    sys.addaudithook(guard)


def priority(row):
    url = unquote(row["canonical_url"]).lower()
    title = unquote(json.dumps([row.get(k) for k in ("canonical_url", "link_label", "title")])).lower()
    context = unquote(json.dumps([row.get(k) for k in ("discovered_from", "references", "source_family_ids")])).lower()
    host = (urlparse(url).hostname or "").lower()
    if re.search(r"clearing|vegetation|vcn[-_]cps|environmental-enforcement|wa-dwer", title + context):
        return None, "unrelated-environmental-clearing-register"
    if host.endswith("acma.gov.au") or "beach-energy" in url:
        return None, "electricity-relevance-not-established"
    if re.search(r"gas[- ](?:retail|licence)|eipn\(g\)|pn\(g\)|sumo-gas", title):
        return None, "gas-specific-document"
    if host in {"acat.act.gov.au", "www.acat.act.gov.au"} and "utility" in title:
        return 0, "utility-tribunal-procedure; energy-and-water scope retained"
    if "wa.gov.au" in host and "western-power" in context:
        return 0, "electricity-network-safety-order"
    if host == "www.escosa.sa.gov.au" and "electricity" in title + context:
        if "application" in title:
            return 3, "electricity-licence-application; not issued licence"
        return 0, "electricity-generation-licence-or-exemption; historical status unreviewed"
    if host == "www.esc.vic.gov.au":
        if "licen" in title and re.search(r"electricity|wholesale", title):
            return 0, "electricity-retail-or-wholesale-licence; historical status unreviewed"
        if "penalt" in title and "vic-esc-penalties" in context:
            return 0, "energy-retailer-penalty-notice; electricity scope requires text review"
        if "licences-and-exemptions" in context:
            return None, "opaque-mixed-gas-electricity-licence-identity-unresolved"
        if ("minister" in title or "stakeholder-letter" in title) and re.search(r"energy|feed-in", title):
            return 1, "electricity-retail-regulatory-correspondence; not operative rule approval"
        if re.search(r"consumer|default-offer|feed.*tariff|energy-retail", context):
            return 3, "electricity-retail-consultation-evidence; not operative rules"
    if host == "www.energysafe.vic.gov.au" and "refcl" in title + context:
        return 2, "electricity-network-REFCL-safety-response; not regulator finding"
    if host == "www.donotcall.gov.au" and "solar-telemarketing" in title:
        return 2, "solar-specific-marketing-compliance-guidance"
    if host == "www.aemc.gov.au" and re.search(r"meter|bidding-in-good-faith|settlement-cycle", context):
        if "private_individual" in title or "j_thompson" in title:
            return None, "private-submission-deferred-for-operative-industry-priority"
        return 3, "electricity-rule-consultation-evidence; not operative rules"
    if host in {"www.qca.org.au", "www.economicregulator.tas.gov.au"} and re.search(r"electric|reliability", title + context):
        return 3, "electricity-consultation-evidence; not operative rules"
    return None, "electricity-document-identity-not-established"


def select(rows, recovered=(), max_docs=MAX_DOCS, max_pages=MAX_PAGES):
    if not 0 < max_docs <= MAX_DOCS or not 0 < max_pages <= MAX_PAGES:
        raise ValueError("Hard bounds: 40 documents / 240 pages")
    eligible, excluded, seen = [], [], set()
    for row in rows:
        rank, reason = priority(row)
        if row["canonical_url"] in recovered or row.get("has_research_text") is not False:
            rank, reason = None, "already-recovered-or-not-current-missing"
        if row.get("capture_status") != "bytes-preserved" or row.get("extraction_status") != "needs-ocr-or-blank-page-review":
            rank, reason = None, "not-required-audit-cohort"
        count = row.get("page_count")
        if type(count) is not int or count <= 0:
            rank, reason = None, "unknown-page-count"
        elif count > 20:
            rank, reason = None, "long-document-deferred-for-short-batch"
        key = (row["canonical_url"], row.get("sha256"))
        if key in seen:
            rank, reason = None, "duplicate-url-and-original"
        seen.add(key)
        if rank is None:
            excluded.append({"reason": reason, "source_record": deepcopy(row)})
        else:
            eligible.append((rank, count, row["canonical_url"], row, reason))
    targets, pages = [], 0
    for rank, count, _, row, reason in sorted(eligible):
        if len(targets) == max_docs or pages + count > max_pages:
            excluded.append({"reason": "document-or-page-budget", "priority": rank, "source_record": deepcopy(row)})
        else:
            targets.append({"prior": deepcopy(row), "page_count": count, "priority": rank, "selection_reason": reason})
            pages += count
    return targets, excluded


def source_inventory():
    # Metadata over every canonical file detects writes/additions; selected input bytes
    # and archive control files are also rehashed at finalization.
    return {p.relative_to(SOURCE).as_posix(): [p.stat().st_size, p.stat().st_mtime_ns]
            for p in SOURCE.rglob("*") if p.is_file()}


def prepare(max_docs, max_pages):
    if (ROOT / "execution.json").exists():
        raise ValueError("Execution already exists; selection cannot change after OCR starts")
    manifest_path = SOURCE / "source-originals/manifest.jsonl"
    audit_path = SOURCE / "review/results/delivery-readiness.json"
    manifest_data, audit_data = manifest_path.read_bytes(), audit_path.read_bytes()
    audit = json.loads(audit_data)
    recorded = [r["sha256"] for r in audit["inputs"] if r.get("role") == "archive" and r.get("path") == "source-originals/manifest.jsonl"]
    if recorded != [sha(manifest_data)]:
        raise ValueError("Readiness audit does not identify the current canonical manifest")
    manifest = [json.loads(line) for line in manifest_data.decode("utf-8-sig").splitlines() if line.strip()]
    latest, recovered = select_manifest_rows(manifest)
    cohort = []
    for item in audit["urls"]:
        if (item["has_research_text"] is False and item.get("capture_status") == "bytes-preserved"
                and item.get("extraction_status") == "needs-ocr-or-blank-page-review"):
            prior = deepcopy(latest[item["canonical_url"]])
            prior.update(has_research_text=False, audit_evidence=deepcopy(item))
            if is_fallback(prior):
                raise ValueError("Missing cohort includes an alternative rather than original source")
            cohort.append(prior)
    targets, excluded = select(cohort, recovered, max_docs, max_pages)
    dump("canonical-before.json", source_inventory())
    for index, target in enumerate(targets, 1):
        prior = target["prior"]
        target.update(id=f"doc-{index:03}", canonical_url=prior["canonical_url"], preparation_status="pending")
        try:
            raw, suffix = verified_original(SOURCE, prior)
            path, digest = save_object(ROOT, raw, suffix)
            target.update(preparation_status="ready", snapshot_path=path, sha256=digest)
        except Exception as exc:
            target.update(preparation_status="failed", preparation_error=f"{type(exc).__name__}: {exc}")
        dump("documents/" + target["id"] + ".json", {
            "id": target["id"], "canonical_url": target["canonical_url"], "status": "not-started",
            "page_count": target["page_count"], "pages": [{"page": p, "locator": f"page:{p}", "render_status": "not-started",
                "first_status": "not-started", "second_status": "not-started"} for p in range(1, target["page_count"] + 1)], **BOUNDARY})
    report = {"targets": targets, "excluded": excluded, "input_missing_urls": len(cohort),
              "selected_documents": len(targets), "selected_pages": sum(t["page_count"] for t in targets),
              "max_documents": max_docs, "max_pages": max_pages, "max_seconds": MAX_SECONDS, "workers": 1,
              "manifest_sha256": sha(manifest_data), "audit_sha256": sha(audit_data),
              "canonical_control_hashes": {str(p.relative_to(SOURCE).as_posix()): sha(p.read_bytes()) for p in (
                  manifest_path, audit_path, SOURCE / "source-originals/search.sqlite3", SOURCE / "data/source-original-inventory.jsonl")},
              "created_at": now(), "network_used": False, **BOUNDARY}
    dump("selection.json", report)
    return {k: v for k, v in report.items() if k not in {"targets", "excluded", "canonical_control_hashes"}}


def comparison(first, second):
    a, b = set(critical_tokens(first)), set(critical_tokens(second))
    # Preserve modal/negation differences separately from the existing numeric tokens.
    words = lambda s: Counter(re.findall(r"\b(?:shall|must|not|may|unless|except|required|prohibited)\b", s.lower()))
    wa, wb = words(first), words(second)
    return {"alphanumeric_similarity": SequenceMatcher(None, re.sub(r"\W", "", first.lower()), re.sub(r"\W", "", second.lower()), autojunk=False).ratio(),
            "tokens_only_in_first": sorted(a - b), "tokens_only_in_second": sorted(b - a),
            "modal_counts_only_in_first": dict(wa - wb), "modal_counts_only_in_second": dict(wb - wa),
            "critical_token_disagreement": bool(a != b or wa != wb)}


def run_worker():
    execution = json.loads((ROOT / "execution.json").read_bytes())
    if execution.get("closed") or not execution["phases"] or execution["phases"][-1]["status"] != "running":
        raise ValueError("Worker requires an active supervisor time reservation")
    sys.path.insert(0, str(PACKAGES))
    import pypdfium2 as pdfium
    import numpy as np
    from rapidocr_onnxruntime import RapidOCR
    from tesserocr import PyTessBaseAPI, PSM, tesseract_version
    reservation = json.loads((ROOT / "execution.json").read_bytes())["phases"][-1]
    if reservation.get("pid") != os.getpid():
        raise ValueError("Worker PID does not match its supervisor reservation")
    rapid = RapidOCR(intra_op_num_threads=2, inter_op_num_threads=1, det_limit_side_len=1280, rec_batch_num=12)
    selection = json.loads((ROOT / "selection.json").read_bytes())
    dump("engines.json", {"first": "rapidocr-onnxruntime-1.4.4", "second": tesseract_version(),
        "renderer": str(pdfium.PYPDFIUM_INFO), "scale": 3.0, "rapidocr_intra_op_threads": 2, "tesseract_thread_limit": 1,
        "native_shortcut_used": False, "tessdata_eng_sha256": sha((TESSDATA / "eng.traineddata").read_bytes()),
        "reused_helpers": {name: sha((STAGE / "scripts" / name).read_bytes()) for name in (
            "recover_scanned_sources.py", "double_extract_scanned_sources.py", "prepare_priority_ocr.py", "recover_preserved_pdf_text.py")}})
    with PyTessBaseAPI(path=str(TESSDATA), lang="eng", psm=PSM.AUTO) as tess:
        for target in sorted(selection["targets"], key=lambda t: (t["page_count"] > 4, t["priority"], t["page_count"], t["id"])):
            relative = "documents/" + target["id"] + ".json"
            record = json.loads((ROOT / relative).read_bytes())
            if record["status"] == "completed":
                continue
            if record["status"] != "not-started":
                attempt_path, attempt_hash = object_json(record)
                record.setdefault("prior_attempts", []).append({"path": attempt_path, "sha256": attempt_hash})
            record.update(status="running", started_at=now())
            dump(relative, record)
            document = None
            try:
                if target["preparation_status"] != "ready":
                    raise ValueError(target.get("preparation_error", "Original not available"))
                raw, _ = verified_original(ROOT, target)
                document = pdfium.PdfDocument(raw)
                if len(document) != target["page_count"]:
                    raise ValueError("PDF page count differs from manifest")
                if pdfium.raw.FPDF_GetSecurityHandlerRevision(document) != -1:
                    raise ValueError("Encrypted PDF deferred; no password attempted")
                for page in record["pages"]:
                    if page["first_status"] == page["second_status"] == "completed":
                        continue
                    for key in ("render_error", "first_error", "second_error"):
                        page.pop(key, None)
                    page.update(render_status="running")
                    dump(relative, record)
                    try:
                        with closing(document[page["page"] - 1]) as source_page:
                            bitmap = source_page.render(scale=3.0)
                            try:
                                pil = bitmap.to_pil().convert("RGB")
                            finally:
                                bitmap.close()
                        buffer = io.BytesIO()
                        pil.save(buffer, format="PNG")
                        path, digest = save_object(ROOT, buffer.getvalue(), ".png")
                        page.update(image_path=path, image_sha256=digest, width=pil.width, height=pil.height, render_status="completed")
                    except Exception as exc:
                        page.update(render_status="failed", render_error=f"{type(exc).__name__}: {exc}", first_status="skipped-render-failed", second_status="skipped-render-failed")
                        dump(relative, record)
                        continue
                    page["first_status"] = "running"
                    dump(relative, record)
                    begin = time.monotonic()
                    try:
                        result, _ = rapid(np.asarray(pil))
                        boxes = [{"box": box, "text": text, "confidence": float(score)} for box, text, score in (result or [])]
                        text = "\n".join(box["text"] for box in boxes)
                        path, digest = object_json([{"locator": page["locator"], "text": text}])
                        page.update(first_status="completed", first_text_path=path, first_text_sha256=digest,
                                    ocr_boxes=boxes, first_empty=not text.strip(), method="rapidocr-onnxruntime-1.4.4")
                    except Exception as exc:
                        page.update(first_status="failed", first_error=f"{type(exc).__name__}: {exc}")
                    page["first_seconds"] = time.monotonic() - begin
                    dump(relative, record)
                    page["second_status"] = "running"
                    dump(relative, record)
                    begin = time.monotonic()
                    try:
                        tess.SetImage(pil)
                        text = tess.GetUTF8Text().strip()
                        path, digest = object_json([{"locator": page["locator"], "text": text}])
                        tsv_path, tsv_digest = save_object(ROOT, tess.GetTSVText(0).encode(), ".tsv")
                        page.update(second_status="completed", second_text_path=path, second_text_sha256=digest,
                                    tesseract_word_boxes_path=tsv_path, tesseract_word_boxes_sha256=tsv_digest,
                                    tesseract_mean_confidence=tess.MeanTextConf(), second_empty=not text.strip())
                    except Exception as exc:
                        page.update(second_status="failed", second_error=f"{type(exc).__name__}: {exc}")
                    page["second_seconds"] = time.monotonic() - begin
                    pil.close()
                    dump(relative, record)
                    print(json.dumps({"document": target["id"], "page": page["page"], "first": page["first_status"], "second": page["second_status"]}), flush=True)
                record["status"] = "completed" if all(p["first_status"] == p["second_status"] == "completed" for p in record["pages"]) else "partial"
            except Exception as exc:
                record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
            finally:
                if document is not None:
                    document.close()
            record["finished_at"] = now()
            dump(relative, record)


def run_batch(seconds):
    if not 0 < seconds <= MAX_SECONDS:
        raise ValueError("OCR process time limit is 1200 seconds")
    selection = json.loads((ROOT / "selection.json").read_bytes())
    if selection["selected_documents"] > MAX_DOCS or selection["selected_pages"] > MAX_PAGES:
        raise ValueError("Saved selection exceeds hard limits")
    execution_path = ROOT / "execution.json"
    execution = json.loads(execution_path.read_bytes()) if execution_path.exists() else {"phases": []}
    if execution.get("closed"):
        raise ValueError("This bounded batch is finalized; no further OCR is permitted")
    if any(p["status"] == "running" for p in execution["phases"]):
        raise ValueError("Unclosed execution reservation; do not start a duplicate worker")
    spent = sum(p["charged_seconds"] for p in execution["phases"])
    allowance = min(seconds, MAX_SECONDS - spent)
    if allowance <= 0:
        return quality_report()
    (ROOT / "tmp").mkdir(parents=True, exist_ok=True)
    phase = {"status": "running", "allowance_seconds": allowance, "charged_seconds": allowance,
             "started_at": now(), "worker_count": 1}
    execution["phases"].append(phase)
    dump("execution.json", execution)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TEMP=str(ROOT / "tmp"), TMP=str(ROOT / "tmp"),
               OMP_THREAD_LIMIT="1", OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1")
    begin = time.monotonic()
    with (ROOT / "worker.log").open("ab") as log:
        process = subprocess.Popen([sys.executable, "-B", str(Path(__file__).resolve()), "worker"], cwd=ROOT, env=env,
                                   stdout=log, stderr=subprocess.STDOUT)
        phase["pid"] = process.pid
        dump("execution.json", execution)
        try:
            process.wait(timeout=max(0.01, allowance - 1))
            phase.update(status="completed" if process.returncode == 0 else "failed", returncode=process.returncode)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            phase.update(status="time-budget-exhausted", returncode=process.returncode)
        except BaseException:
            process.kill()
            process.wait()
            raise
    phase.update(elapsed_seconds=time.monotonic() - begin, finished_at=now())
    # Whole worker lifetime is charged, including rendering, imports and checkpoints:
    # a conservative upper bound on sequential OCR engine time.
    phase["charged_seconds"] = phase["elapsed_seconds"]
    dump("execution.json", execution)
    return quality_report()


def read_page_text(page, prefix):
    path = page.get(prefix + "_text_path")
    return json.loads(contained_path(ROOT, path, objects=True).read_bytes())[0]["text"] if path else ""


def assemble(target, record):
    first, second, selected, evidence, comparisons = [], [], [], [], []
    missing, missing_dual, conflicts, low_pages, single_engine_text = [], [], [], [], []
    for state in record["pages"]:
        page = deepcopy(state)
        for key in ("render_status", "first_status", "second_status"):
            if page[key] == "running":
                page[key] = "interrupted"
            if page[key] == "completed":
                page.pop(key.replace("_status", "_error"), None)
        a, b = read_page_text(page, "first"), read_page_text(page, "second")
        locator = page["locator"]
        first.append({"locator": locator, "text": a})
        second.append({"locator": locator, "text": b})
        chosen = b or a
        selected.append({"locator": locator, "text": chosen})
        if not chosen.strip():
            missing.append(page["page"])
        dual = page["first_status"] == page["second_status"] == "completed"
        if not dual:
            missing_dual.append(page["page"])
            if chosen.strip():
                single_engine_text.append(page["page"])
        page["recovery_state"] = ("dual-ocr-text-unreviewed" if chosen else "empty-needs-blank-page-review") if dual else (
            "partial" if chosen else "not-attempted" if page["render_status"] == "not-started" else "failed-or-interrupted")
        comp = {"page": page["page"], "locator": locator, "dual_engine_completed": dual,
                "first_status": page["first_status"], "second_status": page["second_status"],
                "text_selected_from": "tesseract" if b else "rapidocr-fallback" if a else "neither",
                "tesseract_empty": not bool(b.strip()), "first_empty": not bool(a.strip()),
                "status": "unreviewed-engine-comparison" if dual else "partial-or-unattempted",
                **comparison(a, b)}
        if not dual:
            comp["critical_token_disagreement"] = False
        if comp["critical_token_disagreement"]:
            conflicts.append(page["page"])
        # Recognized nested artifact pairs make BOTH raw page texts and TSV/images
        # traversable by the existing merge/validation helper.
        for prefix, path_key, hash_key in (("first", "alternative_text_path", "alternative_text_sha256"),
                                           ("second", "text_path", "text_sha256")):
            if page.get(prefix + "_text_path"):
                comp[path_key], comp[hash_key] = page[prefix + "_text_path"], page[prefix + "_text_sha256"]
        for key in ("image_path", "image_sha256", "tesseract_word_boxes_path", "tesseract_word_boxes_sha256", "tesseract_mean_confidence"):
            if key in page:
                comp[key] = page[key]
        low_lines = [box for box in page.get("ocr_boxes", []) if box["confidence"] < 0.90]
        low_words = low_confidence_words(contained_path(ROOT, page["tesseract_word_boxes_path"], objects=True).read_text(encoding="utf-8")) if page.get("tesseract_word_boxes_path") else []
        comp.update(rapidocr_low_confidence_lines=low_lines, tesseract_low_confidence_words=low_words,
                    numeric_low_confidence_first_lines=[box for box in low_lines if re.search(r"\d", box["text"])],
                    numeric_low_confidence_second_words=[word for word in low_words if re.search(r"\d", word["text"])])
        if low_lines or low_words:
            low_pages.append(page["page"])
        page.update({k: comp[k] for k in ("alternative_text_path", "alternative_text_sha256", "text_path", "text_sha256") if k in comp})
        evidence.append(page)
        comparisons.append(comp)
    prior = deepcopy(target["prior"])
    for key in list(prior):
        if key.startswith(("text_", "ocr_", "alternative_text_", "extraction_", "recovery_")) or key in {"has_research_text", "audit_evidence"}:
            prior.pop(key)
    first_path, first_hash = object_json(first)
    second_path, second_hash = object_json(second)
    final_path, final_hash = object_json(selected)
    pages_path, pages_hash = object_json(evidence)
    comp_path, comp_hash = object_json(comparisons)
    substantive = sum(substantive_count(u["text"]) for u in selected)
    complete = not missing_dual and not missing and substantive >= 80
    row = {**prior, **BOUNDARY, "id": target["id"], "snapshot_path": target.get("snapshot_path", prior.get("snapshot_path")),
           "sha256": target.get("sha256", prior.get("sha256")), "page_count": target["page_count"],
           "recovery_status": "captured" if complete else "partial" if substantive else "failed",
           "handoff_eligible": len(missing_dual) < target["page_count"] and substantive >= 80,
           "extraction_status": "ocr-extracted-unreviewed" if complete else "needs-ocr-or-blank-page-review",
           "extraction_method": "dual-ocr-rapidocr-tesseract", "extraction_revision": 1,
           "extraction_completeness": "completeness-unreviewed" if complete else "incomplete",
           "text_path": final_path, "text_sha256": final_hash, "alternative_text_path": first_path, "alternative_text_sha256": first_hash,
           "ocr_pages_path": pages_path, "ocr_pages_sha256": pages_hash, "ocr_comparison_path": comp_path, "ocr_comparison_sha256": comp_hash,
           "second_engine_text_path": second_path, "second_engine_text_sha256": second_hash,
           "text_character_count": sum(len(u["text"]) for u in selected), "substantive_character_count": substantive,
           "pages_without_text": missing, "pages_without_dual_ocr": missing_dual,
           "pages_with_single_engine_text": single_engine_text,
           "partial_text_accepted": bool(missing or missing_dual),
           "critical_conflict_pages": conflicts, "low_confidence_pages": low_pages,
           "text_selection_note": "Tesseract preferred mechanically with RapidOCR fallback only for empty second output; neither engine adjudicated.",
           "selection_reason": target["selection_reason"], "ocr_review_status": "critical-fields-and-completeness-not-reviewed",
           "visual_review_status": "not-performed-for-this-document",
           "offline_ocr_provenance": {"source_root": str(SOURCE), "source_snapshot_path": target["prior"].get("snapshot_path"),
               "original_sha256": target["prior"].get("sha256"), "new_download": False, "network_used": False,
               "copied_not_moved": True, "prior_source_record": target["prior"]}}
    # Keep the raw full second extraction reachable using recognized nested refs too.
    comparisons[0]["embedded_record_path"] = second_path
    comparisons[0]["embedded_record_sha256"] = second_hash
    row["ocr_comparison_path"], row["ocr_comparison_sha256"] = object_json(comparisons)
    row["recovery_fingerprint"] = fingerprint(row)
    return row, evidence, comparisons


def quality_report():
    selection = json.loads((ROOT / "selection.json").read_bytes())
    execution = json.loads((ROOT / "execution.json").read_bytes()) if (ROOT / "execution.json").exists() else {"phases": []}
    if any(p["status"] == "running" for p in execution["phases"]):
        raise ValueError("Cannot finalize while OCR worker is reserved/running")
    candidates, documents, checked, errors = [], [], set(), []
    invalid_documents = set()
    conflicts, missing_pages, low_pages = [], [], []
    visual_path = ROOT / "visual-sample.json"
    visual = json.loads(visual_path.read_bytes()) if visual_path.exists() else {"status": "not-performed", "pages": []}
    for target in selection["targets"]:
        record = json.loads((ROOT / "documents" / (target["id"] + ".json")).read_bytes())
        row, pages, comparisons = assemble(target, record)
        sampled = [s["locator"] for s in visual["pages"] if s["id"] == target["id"]]
        if sampled:
            row.update(visual_review_status="bounded-agent-sample-only; not human review", visually_sampled_locators=sampled)
        document_checked, document_errors = set(), []
        check_artifacts(ROOT, row, document_checked, document_errors)
        checked.update(document_checked)
        errors.extend(target["id"] + ": " + e for e in document_errors)
        if document_errors:
            invalid_documents.add(target["id"])
        if row["handoff_eligible"] and not document_errors:
            candidates.append(row)
        doc = {"id": target["id"], "canonical_url": target["canonical_url"], "page_count": target["page_count"],
               "status": row["recovery_status"], "worker_status": "interrupted" if record["status"] == "running" else record["status"],
               "error": record.get("error"), "selection_reason": target["selection_reason"], "artifacts": row, "pages": pages}
        doc["prior_attempts"] = record.get("prior_attempts", [])
        doc["integrity_errors"] = document_errors
        documents.append(doc)
        for comp in comparisons:
            ref = {"id": target["id"], "canonical_url": target["canonical_url"], **comp}
            if comp["critical_token_disagreement"]:
                conflicts.append(ref)
            if comp["rapidocr_low_confidence_lines"] or comp["tesseract_low_confidence_words"]:
                low_pages.append(ref)
            if comp["page"] in row["pages_without_text"] or comp["page"] in row["pages_without_dual_ocr"]:
                missing_pages.append(ref)
    before, after = json.loads((ROOT / "canonical-before.json").read_bytes()), source_inventory()
    changed = [p for p in sorted(set(before) | set(after)) if before.get(p) != after.get(p)]
    controls = {p: sha((SOURCE / p).read_bytes()) == digest for p, digest in selection["canonical_control_hashes"].items()}
    originals_ok = 0
    for target in selection["targets"]:
        try:
            original, _ = verified_original(SOURCE, target["prior"])
            copy, _ = verified_original(ROOT, target)
            if original != copy:
                raise ValueError("Staged original differs")
            originals_ok += 1
        except Exception as exc:
            errors.append(target["id"] + ": " + str(exc))
            invalid_documents.add(target["id"])
    if changed or not all(controls.values()):
        errors.append("Canonical archive changed since baseline")
    object_count, unreferenced_invalid_objects = 0, []
    referenced_paths = {relative for relative, _ in checked}
    for path in (ROOT / "source-originals/objects").rglob("*"):
        if path.is_file():
            object_count += 1
            digest = sha(path.read_bytes())
            if path.stem != digest or path.parent.name != digest[:2]:
                relative = path.relative_to(ROOT).as_posix()
                if relative not in referenced_paths:
                    unreferenced_invalid_objects.append({"path": relative, "actual_sha256": digest,
                        "state": "invalid-unreferenced-object-retained; possible interrupted write"})
                else:
                    errors.append("Invalid immutable hashpath: " + relative)
    for sample in visual["pages"]:
        check_artifacts(ROOT, sample, checked, errors)
    candidates = [r for r in candidates if r["id"] not in invalid_documents]
    if changed or not all(controls.values()):
        candidates = []
    page_rows = [p for d in documents for p in d["pages"]]
    counts = {"input_missing_urls": selection["input_missing_urls"], "selected_documents": len(documents),
        "selected_pages": len(page_rows), "attempted_documents": sum(d["worker_status"] != "not-started" for d in documents),
        "attempted_pages": sum(p["render_status"] != "not-started" for p in page_rows),
        "rendered_pages": sum(p["render_status"] == "completed" for p in page_rows),
        "dual_ocr_pages": sum(p["first_status"] == p["second_status"] == "completed" for p in page_rows),
        "recovered_documents": len(candidates),
        "recovered_text_pages": sum(r["page_count"] - len(r["pages_without_text"]) for r in candidates),
        "handoff_documents_with_missing_text_pages": sum(bool(r["pages_without_text"]) for r in candidates),
        "handoff_documents_with_missing_dual_pages": sum(bool(r["pages_without_dual_ocr"]) for r in candidates),
        "handoff_single_engine_text_pages": sum(len(r["pages_with_single_engine_text"]) for r in candidates),
        "handoff_documents_dual_on_every_page": sum(not r["pages_without_dual_ocr"] for r in candidates),
        "documents_with_text_on_every_page": sum(d["status"] == "captured" for d in documents),
        "partial_documents": sum(d["status"] == "partial" for d in documents),
        "failed_documents": sum(d["status"] == "failed" for d in documents),
        "missing_text_pages": sum(len(d["artifacts"]["pages_without_text"]) for d in documents),
        "missing_dual_ocr_pages": sum(len(d["artifacts"]["pages_without_dual_ocr"]) for d in documents),
        "critical_conflict_pages": len(conflicts), "low_confidence_pages": len(low_pages),
        "visually_sampled_pages": len(visual["pages"]), "excluded_or_deferred_urls": len(selection["excluded"]),
        "original_copies_verified": originals_ok, "integrity_objects_checked": len(checked),
        "all_staged_immutable_objects_rehashed": object_count,
        "invalid_documents_excluded_from_handoff": len(invalid_documents),
        "unreferenced_invalid_objects_retained": len(unreferenced_invalid_objects),
        "remaining_from_cohort_if_merged": selection["input_missing_urls"] - len(candidates)}
    dump("critical-conflicts.json", conflicts)
    dump("missing-pages.json", missing_pages)
    dump("low-confidence.json", low_pages)
    dump("document-outcomes.json", documents)
    dump("invalid-unreferenced-objects.json", unreferenced_invalid_objects)
    log = contained_path(ROOT, FINAL_LOG)
    temporary_log = log.with_suffix(".jsonl.tmp")
    temporary_log.write_text("".join(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n" for row in candidates), encoding="utf-8")
    os.replace(temporary_log, log)
    report = {"generated_at": now(), "counts": counts, "limits": {"documents": MAX_DOCS, "pages": MAX_PAGES, "ocr_engine_seconds": MAX_SECONDS, "workers": 1},
        "execution": execution, "charged_worker_seconds": sum(p["charged_seconds"] for p in execution["phases"]),
        "recorded_completed_engine_seconds": sum(p.get("first_seconds", 0) + p.get("second_seconds", 0) for p in page_rows),
        "batch_status": "finalized-with-partial-extraction" if execution.get("closed") and counts["missing_dual_ocr_pages"] else "dual-ocr-finished" if not counts["missing_dual_ocr_pages"] else "budget-exhausted" if sum(p["charged_seconds"] for p in execution["phases"]) >= MAX_SECONDS - 2 else "partial-retry-available",
        "execution_notes": json.loads((ROOT / "execution-notes.json").read_bytes()) if (ROOT / "execution-notes.json").exists() else [],
        "focused_tests": json.loads((ROOT / "test-results.json").read_bytes()) if (ROOT / "test-results.json").exists() else None,
        "merge_dry_run": json.loads((ROOT / "merge-dry-run.json").read_bytes()) if (ROOT / "merge-dry-run.json").exists() else None,
        "integrity_errors": errors, "canonical_inventory_files_checked": len(before), "canonical_changed_paths": changed,
        "canonical_control_hash_checks": controls, "canonical_archive_unchanged": not changed and all(controls.values()),
        "excluded_reason_counts": dict(Counter(e["reason"] for e in selection["excluded"])),
        "handoff": str(ROOT / FINAL_LOG), "handoff_sha256": sha(log.read_bytes()), "visual_sample": visual,
        "locators": {"selection_and_exclusions": str(ROOT / "selection.json"), "all_document_and_page_states": str(ROOT / "document-outcomes.json"),
            "critical_conflicts": str(ROOT / "critical-conflicts.json"), "missing_pages": str(ROOT / "missing-pages.json"),
            "low_confidence": str(ROOT / "low-confidence.json")},
        "merged": False, "network_used": False, "human_review_performed": False, **BOUNDARY,
        "changed_file_paths": [str(Path(__file__).resolve()), str(STAGE / "review/tests/test_gap_ocr_batch.py"), str(ROOT) + "/**", str(REPORT), str(REPORT.with_suffix(".md"))],
        "caveats": ["Selected titles and types are metadata-based; issuing, commencement, expiry and supersession are not validated.",
            "Tesseract text preference is mechanical; critical conflicts and confidence flags remain unresolved.",
            "Both OCR engines may agree on the same error; neither agreement nor byte checks establish legal accuracy.",
            "Only a bounded agent visual sample is recorded, not full visual or human review.",
            "Blank-looking pages remain missing-text/blank-page-review, never approved as intentionally blank.",
            "Final handoff requires at least one dual-OCR page and 80 substantive document characters; partially extracted documents are accepted with explicit missing-text, missing-dual and single-engine-text page lists.",
            "Canonical unchanged check covers all file size/mtime values plus control-file and selected-original SHA-256; it is not a full archive rehash."]}
    dump("quality-report.json", report)
    REPORT.write_bytes(encoded(report))
    lines = ["# OCR Gap Recovery - 2026-09-07", "", "Research only. No human/legal review or current-law approval.", "",
        *[f"- {k}: {v}" for k, v in counts.items()], "", f"Charged worker lifetime: {report['charged_worker_seconds']:.3f} / 1200 seconds (conservative OCR time bound).",
        f"Canonical unchanged checks: {report['canonical_archive_unchanged']}; integrity errors: {len(errors)}.",
        f"Batch status: {report['batch_status']}.", "",
        "## Handoff and Evidence", "", f"Final merge-preferred JSONL: `{report['handoff']}`", "",
        *[f"- {k}: `{v}`" for k, v in report["locators"].items()], "", "## Documents", "",
        "| ID | Pages | State | Source |", "|---|---:|---|---|",
        *[f"| {d['id']} | {d['page_count']} | {d['status']} | {d['canonical_url']} |" for d in documents], "",
        "## Caveats", "", *["- " + text for text in report["caveats"]], ""]
    REPORT.with_suffix(".md").write_text("\n".join(lines), encoding="utf-8")
    return {k: report[k] for k in ("counts", "charged_worker_seconds", "recorded_completed_engine_seconds", "integrity_errors", "canonical_archive_unchanged", "handoff")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["prepare", "run", "worker", "report", "finalize"])
    parser.add_argument("--max-docs", type=int, default=MAX_DOCS)
    parser.add_argument("--max-pages", type=int, default=MAX_PAGES)
    parser.add_argument("--seconds", type=float, default=MAX_SECONDS)
    args = parser.parse_args()
    guard_writes()
    if args.mode == "worker":
        run_worker()
        return
    if args.mode == "finalize":
        execution = json.loads((ROOT / "execution.json").read_bytes())
        if any(p["status"] == "running" for p in execution["phases"]):
            raise ValueError("Cannot close a running worker")
        execution.update(closed=True, finalized_at=now(),
                         closure_reason="User requested final bounded portion; no further OCR or time extension")
        dump("execution.json", execution)
    result = prepare(args.max_docs, args.max_pages) if args.mode == "prepare" else run_batch(args.seconds) if args.mode == "run" else quality_report()
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
