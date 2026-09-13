"""Read-only, deterministic readiness evidence audit. No legal promotion or fetching."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urldefrag, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
COMPLETE_INDEX = {"complete-case-indexed", "complete-series-indexed"}
BAD_TEXT = {"blocked-or-error-page", "not-extracted", "unsupported-format", "extraction-error"}
ALTERNATIVES = {"current-policy-successor", "current-agency-successor",
                "corrected-official-directory", "public-register-counterpart"}
PENDING = re.compile(
    r"\bpending\b|\bstayed\b|\bstay\s+(?:of|on|in|order)\b|"
    r"\b(?:proceedings|appeal|review)\s+(?:remain[s]?\s+)?(?:ongoing|undetermined)\b",
    re.IGNORECASE,
)


def canonical_url(value):
    """Match collector identity: fragments collapse; queries, paths and schemes do not."""
    if not isinstance(value, str):
        return ""
    try:
        parsed = urlsplit(urldefrag(value.strip())[0])
        if parsed.scheme.lower() not in {"http", "https"} or not parsed.netloc:
            return ""
        return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(),
                           parsed.path, parsed.query, ""))
    except ValueError:
        return ""


def strings(value):
    return [s for s in value if isinstance(s, str) and s.strip()] if isinstance(value, list) else []


def has_review(row):
    return (bool(str(row.get("reviewed_by") or "").strip())
            and bool(str(row.get("reviewed_at") or "").strip())
            and bool(strings(row.get("review_evidence_ids"))))


def family_scope(row, event_count):
    status = row.get("extraction_status", "unknown")
    documented = all(row.get(key) for key in
                     ("source_url", "public_date_scope", "pages_or_years_checked", "checked_at"))
    complete = status in COMPLETE_INDEX and documented and row.get("gap_periods") == []
    count = row.get("public_record_count")
    if type(count) is int and count == 0:
        zero = ("verified-zero-in-ledger-scope" if complete and event_count == 0
                else "aggregate-only-not-zero" if status == "aggregate-only"
                else "unknown-not-zero")
    else:
        zero = "nonzero-recorded" if type(count) is int and count > 0 else "unknown-not-zero"
    return {"ledger_status": status, "public_date_scope": row.get("public_date_scope"),
            "checked_at": row.get("checked_at"), "public_record_count": count,
            "gap_periods": row.get("gap_periods"), "gap_reason": row.get("gap_reason"),
            "registered_public_index_status": "complete-in-ledger-scope" if complete else "not-established",
            "zero_record_interpretation": zero,
            "full_source_family_enumeration": "unknown"}


def select_manifest(rows):
    """Append order is authoritative; a failed retry does not erase preserved text."""
    latest, preserved = {}, {}
    for row in rows:
        url = canonical_url(row.get("canonical_url"))
        if not url:
            continue
        latest[url] = row
        if row.get("invalidates_prior_text") is True:
            preserved.pop(url, None)
        if row.get("text_path") and row.get("extraction_status") not in BAD_TEXT:
            relation = row.get("source_relation") or {}
            # A counterpart may describe the same event without being the same source.
            target = canonical_url(row.get("response_url"))
            alternative = relation.get("kind") in ALTERNATIVES and target != url
            if not alternative:
                preserved[url] = row
    return latest, preserved


def pending_excerpt(value):
    if not isinstance(value, str):
        return None
    match = PENDING.search(value)
    if not match:
        return None
    return value[max(0, match.start() - 100):match.end() + 180].replace("\n", " ")


class Inputs:
    def __init__(self):
        self.provenance = []
        self.issues = []

    def issue(self, code, subject, detail):
        self.issues.append({"code": code, "subject": subject, "detail": detail})

    def read(self, root, relative, kind="json", field=None, role="delivery"):
        path = root / relative
        subject = f"{role}:{relative}"
        try:
            raw = path.read_bytes()
        except OSError:
            self.issue("missing-or-unreadable-input", subject, "Supply the required readable input.")
            self.provenance.append({"role": role, "path": relative, "status": "unavailable"})
            return [] if kind == "jsonl" or field else {} if kind == "json" else ""
        self.provenance.append({"role": role, "path": relative, "sha256": hashlib.sha256(raw).hexdigest(),
                                "size_bytes": len(raw), "status": "read"})
        try:
            text = raw.decode("utf-8-sig")
            if kind == "text":
                return text
            if kind == "jsonl":
                rows = []
                for number, line in enumerate(text.splitlines(), 1):
                    if not line.strip():
                        continue
                    try:
                        row = json.loads(line)
                        if not isinstance(row, dict):
                            raise ValueError("Record must be an object")
                        rows.append(row)
                    except ValueError:
                        self.issue("invalid-jsonl-record", f"{subject}:{number}", "Repair the source record after review.")
                return rows
            result = json.loads(text)
            if not isinstance(result, dict):
                raise ValueError("Expected an object")
            if field:
                result = result.get(field)
                if not isinstance(result, list) or not all(isinstance(row, dict) for row in result):
                    raise ValueError("Expected a list of objects")
            return result
        except (ValueError, UnicodeError):
            self.issue("invalid-input", subject, "Required input has an invalid structure or encoding.")
            return [] if kind == "jsonl" or field else {} if kind == "json" else ""


def text_units(archive_root, row, inputs, cache):
    key = (row.get("text_path"), row.get("text_sha256"))
    if key in cache:
        return cache[key]
    try:
        path = (archive_root / str(key[0])).resolve()
        if not path.is_relative_to((archive_root / "source-originals" / "objects").resolve()):
            raise ValueError("Text path escapes source-originals/objects")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != key[1]:
            raise ValueError("Text hash mismatch")
        units = json.loads(raw)
        if not isinstance(units, list) or not units or not all(
                isinstance(unit, dict) and isinstance(unit.get("text"), str)
                and isinstance(unit.get("locator"), str) and unit["locator"] for unit in units):
            raise ValueError("Text units require text and addressable locators")
        if not any(unit["text"].strip() for unit in units):
            raise ValueError("Text units are empty")
    except (OSError, ValueError, TypeError):
        inputs.issue("unusable-text-object", str(key[0]),
                     "Check archive containment, SHA-256, readable text and unit locators.")
        units = []
    cache[key] = units
    return units


def audit(root, archive_root=None):
    root = Path(root).resolve()
    archive_root = Path(archive_root).resolve() if archive_root else root
    inputs = Inputs()
    inputs.read(root, "README.md", "text")
    inputs.read(root, "ORIGINAL-SOURCE-SCOPE.md", "text")
    register = inputs.read(root, "data/enforcement-source-register.json", field="sources")
    ledger = inputs.read(root, "data/source-coverage-ledger.json")
    reviews = ledger.get("source_reviews", [])
    if not isinstance(reviews, list) or not all(isinstance(row, dict) for row in reviews):
        inputs.issue("invalid-source-reviews", "data/source-coverage-ledger.json", "Expected a list of review objects.")
        reviews = []
    inventory = inputs.read(root, "data/source-original-inventory.jsonl", "jsonl")
    summary = inputs.read(root, "data/source-original-summary.json")
    manifest = inputs.read(archive_root, "source-originals/manifest.jsonl", "jsonl", role="archive")
    manifest_available = inputs.provenance[-1]["status"] == "read"
    events = inputs.read(root, "data/enforcement-events-full.jsonl", "jsonl")
    events += inputs.read(root, "data/technical-events-full.jsonl", "jsonl")
    links = inputs.read(root, "data/event-provision-links.jsonl", "jsonl")
    provisions = inputs.read(root, "data/provision-version-register.json", field="provisions")
    bindings = inputs.read(root, "data/provision-source-bindings.json", field="bindings")
    aliases = inputs.read(root, "data/selected-source-aliases.json", field="aliases")
    resolutions = inputs.read(root, "data/source-recovery-resolution.jsonl", "jsonl")

    def index(rows, field, label):
        result = {}
        for row in rows:
            key = row.get(field)
            if not isinstance(key, str) or not key:
                inputs.issue("missing-record-identity", label, f"A record is missing {field}.")
            elif key in result:
                inputs.issue("duplicate-record-identity", key, f"Duplicate in {label}; review before release.")
            else:
                result[key] = row
        return result

    families = index(register, "id", "source register")
    review_by_id = index(reviews, "source_family_id", "coverage ledger")
    event_by_id = index(events, "event_id", "event files")
    provision_by_id = index(provisions, "provision_id", "provision register")
    binding_by_id = index(bindings, "provision_id", "provision bindings")
    if ledger.get("source_family_count") != len(review_by_id):
        inputs.issue("family-count-mismatch", "coverage ledger", "Declared family count differs from unique review rows.")
    for family in sorted(set(families) ^ set(review_by_id)):
        inputs.issue("family-register-ledger-mismatch", family, "Reconcile source register and coverage review membership.")
    latest, preserved = select_manifest(manifest)
    urls = {}

    def add_url(value, family_ids=(), reference=None):
        url = canonical_url(value)
        if not url:
            if value:
                inputs.issue("invalid-source-url", str(value), "Review the explicit source URL.")
            return None
        item = urls.setdefault(url, {"family_ids": set(), "references": set(), "url_forms": set(), "inventory": None})
        item["family_ids"].update(family for family in family_ids if isinstance(family, str) and family)
        item["url_forms"].add(value)
        if reference:
            item["references"].add(reference)
        return item

    for row in inventory + manifest:
        item = add_url(row.get("canonical_url"), strings(row.get("source_family_ids")))
        if item is None:
            inputs.issue("missing-record-identity", "source inventory/manifest", "A row needs a valid canonical_url.")
            continue
        item["references"].update(strings(row.get("references")))
    for row in inventory:
        item = urls.get(canonical_url(row.get("canonical_url")))
        if item is not None:
            if item["inventory"] is not None and item["inventory"] != row:
                inputs.issue("duplicate-inventory-url", row["canonical_url"], "Reconcile inventory rows after fragment normalization.")
            item["inventory"] = row
    for family, row in families.items():
        add_url(row.get("url"), [family], f"source-family:{family}")
    for family, row in review_by_id.items():
        add_url(row.get("source_url"), [family], f"coverage-review:{family}")
    for event_id, row in event_by_id.items():
        add_url(row.get("official_source_url"), [row.get("source_family_id")], f"event:{event_id}")
    for provision_id, row in provision_by_id.items():
        add_url(row.get("official_url"), reference=f"provision:{provision_id}")
    for row in aliases:
        family_ids = [event_by_id[event_id].get("source_family_id")
                      for event_id in strings(row.get("canonical_event_ids")) if event_id in event_by_id]
        add_url(row.get("alias_url"), family_ids, "selected-event-source-alias")
        for event_id in strings(row.get("canonical_event_ids")):
            if event_id not in event_by_id:
                inputs.issue("alias-event-missing", event_id, "Selected-source alias references an absent canonical event.")
    replacements = []
    for row in resolutions:
        if row.get("status") == "alternative-official-source-only":
            original = canonical_url(row.get("canonical_url"))
            replacement = canonical_url(row.get("response_url"))
            add_url(original)
            add_url(replacement)
            replacements.append({"original_url": original, "replacement_url": replacement,
                                 "source_relation": row.get("source_relation"),
                                 "closes_original_gap": False})

    tasks, candidates = [], []

    def task(code, subject, action, family_ids=()):
        tasks.append({"task": code, "subject": subject, "source_family_ids": sorted(set(family_ids)), "action": action})

    def candidate(code, event_id, evidence, layer):
        candidates.append({"code": code, "event_id": event_id, "layer": layer,
                           "structured_status": event_by_id.get(event_id, {}).get("status"),
                           "evidence": evidence, "disposition": "review-candidate",
                           "automatic_legal_reclassification": False})

    url_rows, cache, units_by_url = [], {}, {}
    for url, item in sorted(urls.items()):
        family_ids = sorted(item["family_ids"])
        inv = item["inventory"] or {}
        saved = preserved.get(url)
        current = latest.get(url, {})
        units = text_units(archive_root, saved, inputs, cache) if saved else []
        units_by_url[url] = units
        has_text = bool(units) if manifest_available else inv.get("has_research_text") is True
        basis = "archive-text-hash-and-locators" if manifest_available else "inventory-claim-only"
        status = (saved or current).get("extraction_status") if manifest_available else inv.get("latest_extraction_status")
        no_text_pages = list((saved or current).get("pages_without_text") or [])
        page_count = (saved or current).get("page_count")
        if units and type(page_count) is int and page_count > 0:
            found = {int(m.group(1)) for unit in units if unit["text"].strip()
                     and (m := re.fullmatch(r"page:(\d+)", unit["locator"]))}
            no_text_pages = sorted(set(no_text_pages) | (set(range(1, page_count + 1)) - found))
        needs_ocr = bool(no_text_pages) or status in {"needs-ocr-or-blank-page-review", "ocr-extracted-unreviewed"}
        extraction_state = ("missing-text" if not has_text else "needs-ocr-or-blank-page-review" if needs_ocr
                            else "needs-browser-or-content-review" if status == "needs-browser-rendering-or-content-review"
                            else "completeness-unreviewed")
        if inv and manifest_available and (inv.get("has_research_text") is True) != has_text:
            inputs.issue("inventory-archive-text-mismatch", url, "Reconcile the inventory claim with the selected preserved text object.")
        if not has_text:
            task("recover-known-source-text", url, "Review the recorded access/extraction failure; preserve the exact source using permitted access.", family_ids)
        if needs_ocr:
            task("ocr-or-blank-page-review", url, "Check all missing pages and compare critical OCR fields against the page images.", family_ids)
        if has_text:
            task("review-extraction-completeness", url, "Check substantive pages, footnotes, appendices, attachments and representation against the source.", family_ids)
        if not family_ids:
            task("review-source-family-membership", url, "Review relevance and assign an evidenced source family; do not infer membership from hostname.")
        url_rows.append({"canonical_url": url, "source_family_ids": family_ids,
                         "url_forms": sorted(item["url_forms"]), "references": sorted(item["references"]),
                         "has_research_text": has_text, "text_evidence_basis": basis,
                         "capture_status": current.get("capture_status", inv.get("latest_capture_status", "not-recorded")),
                         "reason": current.get("reason", inv.get("latest_reason")),
                         "extraction_status": status, "extraction_completeness": extraction_state,
                         "needs_ocr_or_blank_page_review": needs_ocr, "pages_without_text": no_text_pages,
                         "legal_review_status": (saved or current).get("legal_review_status", "not-established"),
                         "current_law_release_claim": (saved or current).get("current_law_release") is True,
                         "source_relation": (saved or current).get("source_relation")})
    for row in replacements:
        task("review-replacement-identity", row["original_url"],
             f"Keep the original gap visible; review the separately identified alternative: {row['replacement_url']}")

    links_by_event = defaultdict(list)
    for row in links:
        links_by_event[row.get("event_id")].append(row)
    association_rows = []
    for event_id, event in sorted(event_by_id.items()):
        event_links = links_by_event.get(event_id, [])
        reasons = []
        if len(event_links) != 1:
            reasons.append("missing-link" if not event_links else "duplicate-links")
        for link in event_links:
            # Candidate status is never overridden by filled-in reviewer fields.
            if link.get("review_status") != "independently-approved" or not has_review(link):
                reasons.append("association-not-independently-approved")
            comparators = strings(link.get("current_comparator_ids"))
            if not comparators:
                reasons.append("no-comparator-or-reviewed-disposition")
            if any(provision_id not in provision_by_id for provision_id in comparators):
                reasons.append("missing-provision-reference")
            if link.get("historical_status") != event.get("status"):
                candidate("event-link-status-mismatch", event_id,
                          {"event_status": event.get("status"), "link_historical_status": link.get("historical_status")},
                          "canonical-event/event-provision-link")
                reasons.append("event-link-status-mismatch")
        association_rows.append({"event_id": event_id, "review_established": not reasons,
                                 "reasons": sorted(set(reasons))})
        if reasons:
            task("review-case-provision-association", event_id,
                 "Review exact historical provision, source version/locator, current comparator, jurisdiction and procedural status; record independent approval.",
                 [event["source_family_id"]] if event.get("source_family_id") else [])
        if str(event.get("status", "")).startswith("final"):
            for field in ("issue", "outcome", "case_status_note"):
                excerpt = pending_excerpt(event.get(field))
                if excerpt:
                    candidate("final-status-pending-or-stay-language", event_id, {"field": field, "excerpt": excerpt}, "canonical-event")
            for link in event_links:
                for field in ("historical_status", "current_authority_note"):
                    excerpt = pending_excerpt(link.get(field))
                    if excerpt:
                        candidate("final-status-pending-or-stay-language", event_id,
                                  {"field": field, "excerpt": excerpt}, "event-provision-link")
            url = canonical_url(event.get("official_source_url"))
            for unit in units_by_url.get(url, []):
                excerpt = pending_excerpt(unit["text"])
                if excerpt:
                    candidate("final-status-source-pending-or-stay-language", event_id,
                              {"canonical_url": url, "locator": unit["locator"], "excerpt": excerpt,
                               "scope_note": "Source-level signal may concern another event or an ended stay; review chronology and identity."},
                              "preserved-source-text")
                    break
    for event_id in sorted(set(links_by_event) - set(event_by_id), key=str):
        inputs.issue("orphan-event-link", str(event_id), "Link references an absent canonical event.")
        task("review-orphan-event-link", str(event_id), "Reconcile this link with the canonical event register.")

    all_families = set(families) | set(review_by_id) | {f for row in url_rows for f in row["source_family_ids"]}
    event_counts = Counter(row.get("source_family_id") for row in event_by_id.values())
    family_rows = []
    for family in sorted(all_families):
        family_urls = [row for row in url_rows if family in row["source_family_ids"]]
        text_count = sum(row["has_research_text"] for row in family_urls)
        scope = family_scope(review_by_id.get(family, {}), event_counts[family])
        if family not in families:
            inputs.issue("unregistered-source-family", family, "Review referenced family identity against the source register.")
        if scope["public_record_count"] == 0 and event_counts[family]:
            inputs.issue("zero-count-event-conflict", family, "Zero ledger count conflicts with canonical events in this family.")
        family_rows.append({"source_family_id": family, "known_url_count": len(family_urls),
                            "text_url_count": text_count, "missing_text_url_count": len(family_urls) - text_count,
                            "needs_ocr_url_count": sum(row["needs_ocr_or_blank_page_review"] for row in family_urls),
                            "canonical_event_count": event_counts[family], **scope})
        task("enumerate-full-source-family", family,
             "Reconcile all in-scope indexes, pagination, periods, versions and attachments with publisher totals and archive boundaries; record exclusions and gaps.", [family])

    for provision_id, provision in sorted(provision_by_id.items()):
        binding = binding_by_id.get(provision_id, {})
        if not (binding.get("supports_current_law_drafting") is True
                and strings(binding.get("source_span_ids")) and strings(binding.get("source_locators"))
                and strings(binding.get("source_sha256_values"))):
            task("review-provision-source-binding", provision_id,
                 "Review exact clause text, immutable source spans, effective dates and applicability before any current-law use.")
    task("establish-source-universe", "all-required-source-classes",
         "Reconcile the ORIGINAL-SOURCE-SCOPE jurisdiction/document-class census, including families not in the enforcement register.")
    task("independent-legal-verification", "delivery",
         "Obtain source-bound legal and temporal review for the intended claims; research text and drafting flags are insufficient.")
    task("operational-release-approval", "delivery",
         "Record accountable approval for a defined action, date, permissions and tested handover; this audit does not grant release.")
    for issue in inputs.issues:
        task("resolve-input-defect", issue["subject"], issue["detail"])
    for row in candidates:
        task("review-status-conflict-candidate", row["event_id"],
             "Check the cited layers, event identity, timeline and appeal/stay disposition; do not automatically reclassify the event.")
    # Identical action rows are collapsed, while each distinct evidence candidate is retained.
    tasks = sorted({json.dumps(row, sort_keys=True): row for row in tasks}.values(),
                   key=lambda row: (row["task"], row["subject"]))
    for family in family_rows:
        family["task_counts"] = dict(sorted(Counter(
            row["task"] for row in tasks if family["source_family_id"] in row["source_family_ids"]
        ).items()))
    known = len(url_rows)
    text_count = sum(row["has_research_text"] for row in url_rows)
    association_complete = (bool(event_by_id) and len(links) == len(event_by_id)
                            and all(row["review_established"] for row in association_rows) and not candidates)
    gates = {
        "input_evidence": {"status": "established" if not inputs.issues else "not-established"},
        "known_url_text_coverage": {"status": "complete-known-queue" if known and text_count == known else "incomplete",
                                    "basis": "archive-text-objects" if manifest_available else "inventory-claims-only"},
        "extraction_completeness": {"status": "not-established", "reason": "No per-source visual completeness approvals are established by this audit."},
        "full_source_family_enumeration": {"status": "unknown", "reason": "The enforcement ledger and known URL inventory do not define the full original-source universe."},
        "case_provision_association_review": {"status": "established" if association_complete else "not-established"},
        "legal_verification": {"status": "not-established", "reason": "Text acquisition, current-at-baseline labels and drafting flags do not establish independent legal verification."},
        "operational_release": {"status": "not-established", "reason": "No action-specific accountable release approval is certified by this read-only audit."},
    }
    blocking_gates = [key for key, value in gates.items()
                      if value["status"] not in {"established", "complete-known-queue"}]
    return {
        "schema_version": "1.0", "audit_kind": "deterministic-delivery-readiness-evidence",
        "delivery_ready": not blocking_gates,
        "decision_boundary": "This scoped auditor has no approval mechanism for full enumeration, visual completeness, legal verification or operational execution. It reports missing evidence and cannot grant release.",
        "baseline_date": ledger.get("baseline_date"),
        "archive_root": str(archive_root), "archive_available": manifest_available,
        "inputs": inputs.provenance, "input_defects": inputs.issues,
        "gates": gates, "blocking_gates": blocking_gates,
        "counts": {"known_url_count": known, "text_url_count": text_count,
                   "missing_text_url_count": known - text_count,
                   "inventory_unique_url_count": len({canonical_url(row.get("canonical_url")) for row in inventory} - {""}),
                   "inventory_summary_url_count_claim": summary.get("inventory_url_count"),
                   "inventory_summary_text_count_claim": summary.get("research_text_url_count"),
                   "archive_verified_text_url_count": text_count if manifest_available else 0,
                   "unassigned_family_url_count": sum(not row["source_family_ids"] for row in url_rows),
                   "cross_family_url_count": sum(len(row["source_family_ids"]) > 1 for row in url_rows),
                   "family_membership_url_count": sum(len(row["source_family_ids"]) for row in url_rows),
                   "needs_ocr_url_count": sum(row["needs_ocr_or_blank_page_review"] for row in url_rows),
                   "source_family_count": len(family_rows), "event_count": len(event_by_id),
                   "link_count": len(links), "reviewed_association_count": sum(row["review_established"] for row in association_rows),
                   "review_candidate_count": len(candidates)},
        "task_counts": dict(sorted(Counter(row["task"] for row in tasks).items())),
        "families": family_rows, "urls": url_rows, "associations": association_rows,
        "replacement_sources": sorted(replacements, key=lambda row: row["original_url"]),
        "review_candidates": candidates, "tasks": tasks,
    }


def markdown(report):
    counts = report["counts"]
    readiness = "established" if report["delivery_ready"] else "not established"
    lines = ["# Delivery Readiness Audit", "", f"Delivery ready: **{readiness}**.", "",
             report["decision_boundary"], "",
             f"Known URLs: {counts['known_url_count']}; research text: {counts['text_url_count']}; missing text: {counts['missing_text_url_count']}.",
             f"Text evidence: {report['gates']['known_url_text_coverage']['basis']}. OCR/blank-page review: {counts['needs_ocr_url_count']} URLs.",
             "Global URL counts are unique. Family membership counts may overlap. Missing/unassigned families remain visible.", "",
             "| Gate | Status |", "|---|---|"]
    lines.extend(f"| {name} | {gate['status']} |" for name, gate in report["gates"].items())
    lines.extend(["", "## Source Families", "",
                  "Verified zero is a ledger claim within its stated public-index scope, never a claim that no violations or other source classes exist.", "",
                  "| Family | Known | Text | Missing | OCR review | Ledger | Zero interpretation | Full enumeration |",
                  "|---|---:|---:|---:|---:|---|---|---|"])
    for row in report["families"]:
        lines.append(f"| {row['source_family_id']} | {row['known_url_count']} | {row['text_url_count']} | {row['missing_text_url_count']} | {row['needs_ocr_url_count']} | {row['ledger_status']} | {row['zero_record_interpretation']} | unknown |")
    lines.extend(["", "## Action Queue", "", "| Task | Count |", "|---|---:|"])
    lines.extend(f"| {name} | {count} |" for name, count in report["task_counts"].items())
    lines.extend(["", "## Review Candidates", "",
                  f"{counts['review_candidate_count']} evidence signals; none automatically change legal status.",
                  "Pending/stay language may concern historical proceedings or another event on a shared source. Review identity and chronology.",
                  "See delivery-review-candidates.jsonl for source locators and excerpts, delivery-tasks.jsonl for actions, and delivery-readiness.json for all counters, URLs and input hashes.", ""])
    return "\n".join(lines).encode("ascii", "backslashreplace").decode("ascii")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Delivery root; canonical inputs are read-only.")
    parser.add_argument("--archive-root", type=Path, help="Read-only KB root containing source-originals/manifest.jsonl and objects.")
    parser.add_argument("--output-dir", type=Path, help="Output directory under the delivery root's review/results.")
    parser.add_argument("--require-ready", action="store_true", help="Return 1 unless delivery readiness is established; still write reports.")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    output = (args.output_dir or root / "review" / "results").resolve()
    if not output.is_relative_to((root / "review" / "results").resolve()):
        parser.error("--output-dir must stay under the delivery root's review/results")
    report = audit(root, args.archive_root)
    output.mkdir(parents=True, exist_ok=True)
    for name in ("delivery-readiness.json", "delivery-readiness.md", "delivery-tasks.jsonl", "delivery-review-candidates.jsonl"):
        if (output / name).is_symlink():
            parser.error("Refusing to overwrite a report symlink")
    (output / "delivery-readiness.json").write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="ascii")
    (output / "delivery-readiness.md").write_text(markdown(report), encoding="ascii")
    for name, key in (("delivery-tasks.jsonl", "tasks"), ("delivery-review-candidates.jsonl", "review_candidates")):
        (output / name).write_text("".join(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n" for row in report[key]), encoding="ascii")
    print(json.dumps({"delivery_ready": report["delivery_ready"], "counts": report["counts"],
                      "blocking_gates": report["blocking_gates"], "output_dir": str(output)}, sort_keys=True))
    return 1 if args.require_ready and not report["delivery_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
