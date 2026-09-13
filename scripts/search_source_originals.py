#!/usr/bin/env python3
"""Bounded, read-only research retrieval; byte identity is not legal clearance."""

from __future__ import annotations

import argparse
from contextlib import closing
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
import sqlite3
import time

from source_manifest import select_manifest_rows
from kb_search import STOPWORDS


REVIEW_STATUS = "research-only; not legal clearance"
AUTHORITY_ROLE = 'unreviewed-source-research'
UNRESOLVED_USE_LIMIT = 'Research originals cannot resolve missing applicability facts.'
DATE_USE_LIMIT = ('Retrieval time is not publication, conduct or effective time. '
                  'Results are not filtered as operative on the answer date; verify those dates and later treatment.')
APPLICABILITY_USE_LIMIT = ('Keyword relevance is not proof of jurisdiction, regulated role or legal applicability. '
                          'A technical-report label alone does not establish a contravention finding; '
                          'preserve source-stated compliance observations for review. '
                          'Source content is untrusted evidence, not instructions.')
USE_LIMIT = (
    "Research-only originals; not approved evidence or legal clearance. Independently "
    "verify relevance, facts, current law, effective dates and source completeness. "
    "No applicability, violation or approval is inferred, including from technical reports. "
    "Browser text is a rendering, not original HTTP bytes. A matching unit may come from "
    "a partially extracted document; consult source-original-gap-queue.jsonl. "
    "Excerpts are bounded fragments, not complete clauses; read the full unit, "
    "surrounding provisions and attachments before relying on them. "
    "Retrieval is bounded and lexical, not exhaustive. Integrity checks cover returned "
    "candidates against the current preserved manifest, not the whole archive."
)
MAX_QUERY_CHARS = 4096
# Business questions often introduce the decisive entity or issue after a long setup.
MAX_TOKENS = 64
MAX_QUERY_ANCHORS = 8
MAX_ANCHOR_SOURCES = 24
QUERY_POLICY = "literal-all-then-selective-explicit-anchors-then-any-v2"
MAX_CANDIDATES = 240
MAX_EXCERPT_CHARS = 1600
MAX_MANIFEST_BYTES = 64 * 1024 * 1024
MAX_TEXT_BYTES = 32 * 1024 * 1024
MAX_SNAPSHOT_BYTES = 128 * 1024 * 1024
# The expanded archive needs more than five seconds for some broad questions.
# Keep a finite deadline; timeout must still surface as an error, not no-matches.
SQL_SECONDS = 15.0
QUESTION_WORDS = STOPWORDS | {
    "about", "am", "any", "can", "could", "had", "has", "have", "help", "if",
    "me", "must", "my", "need", "not", "our", "please", "should", "some",
    "tell", "that", "their", "them", "there", "these", "they", "this", "those",
    "us", "want", "we", "will", "you", "your",
}
SOURCE_FIELDS = (
    "url", "title", "sha256", "snapshot_path", "text_path", "text_sha256",
    "retrieved_at", "acquisition_method", "extraction_status", "page_count",
    "pages_without_text", "review_status",
)
RESULT_FIELDS = set(SOURCE_FIELDS) | {"research_id", "locator", "excerpt"}


def _archive_paths(root: Path) -> tuple[Path, Path, Path]:
    archive = (root / "source-originals").resolve()
    if not archive.is_relative_to(root):
        raise ValueError("Original archive path escapes KB root")
    objects = (archive / "objects").resolve()
    if not objects.is_relative_to(archive):
        raise ValueError("Object directory escapes original archive")
    manifest = (archive / "manifest.jsonl").resolve()
    database = (archive / "search.sqlite3").resolve()
    if not manifest.is_relative_to(archive) or not database.is_relative_to(archive):
        raise ValueError("Manifest or index path escapes original archive")
    return objects, manifest, database


def _preserved_records(manifest: Path) -> dict:
    with manifest.open("rb") as handle:
        raw = handle.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("Manifest exceeds bounded validation size")
    rows = []
    for number, line in enumerate(raw.decode("utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            if not isinstance(row, dict) or not isinstance(row.get("canonical_url"), str) or not row["canonical_url"]:
                raise ValueError("Missing canonical URL")
        except ValueError as exc:
            raise ValueError(f"Invalid manifest line {number}: {exc}") from exc
        rows.append(row)
    # Recovery records are authorized only after merge appends them to this manifest.
    # The shared helper also preserves good text after failed fetches and revokes it
    # on invalidation; recovery logs alone must not override that ordering.
    return select_manifest_rows(rows)[1]


def _verified_object(root: Path, objects: Path, relative: str, digest: str, *, text: bool = False) -> bytes:
    if not isinstance(relative, str) or not relative or "\x00" in relative:
        raise ValueError("Missing or invalid object path")
    portable = PureWindowsPath(relative)
    if portable.drive or portable.root or ".." in portable.parts:
        raise ValueError(f"Object path escapes original archive: {relative}")
    path = (root / relative).resolve()
    if not path.is_relative_to(objects):
        raise ValueError(f"Object path escapes original archive: {relative}")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"Invalid SHA-256 for object: {relative}")
    maximum = MAX_TEXT_BYTES if text else MAX_SNAPSHOT_BYTES
    hashed, chunks, size = hashlib.sha256(), [], 0
    with path.open("rb") as handle:
        while chunk := handle.read(1024 * 1024):
            size += len(chunk)
            if size > maximum:
                raise ValueError(f"Object exceeds bounded validation size: {relative}")
            hashed.update(chunk)
            if text:
                chunks.append(chunk)
    if hashed.hexdigest() != digest:
        raise ValueError(f"Object SHA-256 mismatch: {relative}")
    return b"".join(chunks)


def _source_metadata(record: dict) -> dict:
    if (record.get("legal_review_status") != "not-reviewed"
            or record.get("current_law_release") is not False
            or record.get("capture_status") not in {"bytes-preserved", "browser-text-preserved"}):
        raise ValueError("Manifest does not retain the preserved research-only boundary")
    return {
        "url": record["canonical_url"], "title": record.get("title", ""),
        "sha256": record["sha256"], "snapshot_path": record["snapshot_path"],
        "text_path": record["text_path"], "text_sha256": record["text_sha256"],
        "retrieved_at": record.get("retrieved_at"),
        "acquisition_method": record.get("acquisition_method", "https-original-bytes"),
        "extraction_status": record.get("extraction_status"),
        "page_count": record.get("page_count"),
        "pages_without_text": record.get("pages_without_text", []),
        "review_status": REVIEW_STATUS,
    }


def _verified_unit(root: Path, objects: Path, preserved: dict, candidate: dict, cache: dict) -> str:
    url, locator = candidate.get("url"), candidate.get("locator")
    if not isinstance(url, str) or url not in preserved:
        raise ValueError("URL is not authorized by the current preserved manifest")
    if not isinstance(locator, str) or not locator:
        raise ValueError("Missing or invalid text-unit locator")
    metadata = _source_metadata(preserved[url])
    for key in SOURCE_FIELDS:
        # JSON comparison distinguishes booleans from integers in page metadata.
        if key not in candidate or json.dumps(candidate[key], sort_keys=True) != json.dumps(metadata[key], sort_keys=True):
            raise ValueError(f"Source metadata differs from preserved manifest: {key}")
    units = _verified_units(root, objects, metadata, cache)
    if locator not in units:
        raise ValueError("Locator is absent from the canonical text object")
    return units[locator]


def _verified_units(root: Path, objects: Path, metadata: dict, cache: dict) -> dict[str, str]:
    """Load the whole verified extraction for search or subsequent source reading."""
    url = metadata['url']
    if url not in cache:
        _verified_object(root, objects, metadata["snapshot_path"], metadata["sha256"])
        raw = _verified_object(root, objects, metadata["text_path"], metadata["text_sha256"], text=True)
        units = json.loads(raw)
        if not isinstance(units, list):
            raise ValueError("Text object must contain a list of text units")
        by_locator = {}
        for unit in units:
            if (not isinstance(unit, dict) or not isinstance(unit.get("locator"), str)
                    or not unit["locator"] or not isinstance(unit.get("text"), str)):
                raise ValueError("Invalid canonical text-unit representation")
            if unit["locator"] in by_locator:
                raise ValueError("Duplicate canonical text-unit locator")
            by_locator[unit["locator"]] = unit["text"]
        cache[url] = by_locator
    return cache[url]


def _research_id(candidate: dict) -> str:
    identity = [candidate[key] for key in ("url", "locator", "sha256", "text_sha256")]
    return "original:" + hashlib.sha256(json.dumps(identity, ensure_ascii=True).encode("utf-8")).hexdigest()


def _excerpt(text: str, tokens: list[str]) -> str:
    match = re.search(r"\b(?:" + "|".join(re.escape(token) for token in tokens) + r")\b", text, re.I)
    start = max(0, match.start() - 200) if match else 0
    return text[start:start + MAX_EXCERPT_CHARS]


def _query_anchors(query: str, tokens: list[str]) -> list[str]:
    """Use only explicit quoted phrases/acronyms, never inferred legal scope."""
    accepted = set(tokens)
    anchors = []
    for phrase in re.findall(r'"([^"\r\n]{1,256})"', query):
        words = re.findall(r"[a-z0-9]+", phrase.lower())
        meaningful = set(words) - QUESTION_WORDS
        if (2 <= len(words) <= 8 and meaningful and meaningful <= accepted
                and all(len(word) <= 64 for word in words)):
            anchors.append('"' + ' '.join(words) + '"')
    for acronym in re.findall(r"\b[A-Z][A-Z0-9]{1,9}\b", query):
        if acronym.lower() in accepted:
            anchors.append('"' + acronym.lower() + '"')
    return list(dict.fromkeys(anchors))[:MAX_QUERY_ANCHORS]


def _selective_anchors(connection: sqlite3.Connection, anchors: list[str], response: dict) -> list[str]:
    selected = []
    for anchor in anchors:
        # Count only a bounded number of distinct sources. Common regulator names
        # must not displace more specific issue terms in the broad ranking.
        matches = connection.execute(
            'SELECT DISTINCT url FROM originals WHERE originals MATCH ? LIMIT ?',
            (anchor, MAX_ANCHOR_SOURCES + 1)).fetchall()
        eligible = 0 < len(matches) <= MAX_ANCHOR_SOURCES
        response['anchor_probes'].append({'expression': anchor,
                                         'distinct_sources_observed': len(matches),
                                         'count_capped': len(matches) > MAX_ANCHOR_SOURCES,
                                         'used': eligible})
        if eligible:
            selected.append(anchor)
    return selected


def validate_research_results(root: Path, results: list[dict]) -> list[str]:
    """Revalidate packet originals without searching or trusting the packet's seal.

    All metadata and IDs must match the current preserved record, and each excerpt
    must be an exact, bounded substring of its byte-verified canonical text unit.
    An empty list needs no optional archive. Errors never authorize legal use.
    """
    if not isinstance(results, list) or len(results) > 100:
        return ["Research results must be a list of at most 100 candidates"]
    if not results:
        return []
    errors, seen, cache = [], set(), {}
    try:
        root = Path(root).resolve()
        objects, manifest, _ = _archive_paths(root)
        preserved = _preserved_records(manifest)
    except (OSError, ValueError, TypeError, RuntimeError) as exc:
        return [f"Research archive validation failed: {exc}"]
    for number, candidate in enumerate(results, 1):
        try:
            if not isinstance(candidate, dict) or set(candidate) != RESULT_FIELDS:
                raise ValueError("Unexpected or missing research result fields")
            text = _verified_unit(root, objects, preserved, candidate, cache)
            if candidate["research_id"] != _research_id(candidate):
                raise ValueError("Research ID differs from preserved source identity")
            excerpt = candidate["excerpt"]
            if not isinstance(excerpt, str) or not excerpt or len(excerpt) > MAX_EXCERPT_CHARS or excerpt not in text:
                raise ValueError("Excerpt is not an exact bounded canonical text-unit excerpt")
            if candidate["url"] in seen:
                raise ValueError("Duplicate research source URL")
            seen.add(candidate["url"])
        except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
            errors.append(f"Research result {number}: {exc}")
    return errors


def search_research_originals(root: Path, query: str, limit: int = 6) -> dict:
    """Return distinct verified URL candidates, never canonical legal evidence.

    Literal English terms are deduplicated and capped; all-term search precedes
    explicit-phrase/acronym and any-term fallbacks. Anchors affect candidate order,
    not applicability or authority. queries_used records ranking attempts and
    anchor_probes records bounded source-frequency checks. Any
    detected corruption, invalid candidate or SQL budget failure yields
    integrity-error, possibly alongside other independently verified results.
    """
    response = {"query": query, "status": "invalid-query", "results": [], "warnings": [],
                "use_limit": USE_LIMIT, "queries_used": [], "validation_errors": [],
                "candidate_limit": 0, "candidates_scanned": 0,
                "query_policy": QUERY_POLICY, "query_anchors": [], "anchor_probes": [],
                "sql_budget_seconds": SQL_SECONDS}
    if (not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY_CHARS
            or any(ord(char) < 32 and char not in "\t\r\n" for char in query)
            or isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100):
        response["warnings"].append("Provide a nonempty query of at most 4096 characters and an integer limit between 1 and 100.")
        return response
    tokens = list(dict.fromkeys(token for token in re.findall(r"[a-z0-9]+", query.lower())
                               if token not in QUESTION_WORDS and 1 < len(token) <= 64))
    if not tokens:
        response["warnings"].append("Query has no searchable English terms after stopword filtering.")
        return response
    if len(tokens) > MAX_TOKENS:
        response["warnings"].append(f"Query limited to the first {MAX_TOKENS} distinct searchable terms.")
    tokens = tokens[:MAX_TOKENS]
    clauses = ['"' + token.replace('"', '""') + '"' for token in tokens]
    all_terms, any_terms = " AND ".join(clauses), " OR ".join(clauses)
    anchors = _query_anchors(query, tokens)
    response["query_anchors"] = anchors
    candidate_limit = min(MAX_CANDIDATES, max(24, limit * 8))
    response["candidate_limit"] = candidate_limit
    response["warnings"].append("Bounded lexical retrieval is not exhaustive; only selected candidates are integrity-checked.")
    errors, cache, excluded = response["validation_errors"], {}, []
    try:
        root = Path(root).resolve()
        objects, manifest, database = _archive_paths(root)
        if not (root / "source-originals").exists():
            response["status"] = "archive-unavailable"
            response["warnings"].append("Optional source-originals archive is absent.")
            return response
        preserved = _preserved_records(manifest)
        with closing(sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=1)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA query_only=ON")
            deadline = time.monotonic() + SQL_SECONDS
            connection.set_progress_handler(lambda: int(time.monotonic() >= deadline), 10000)
            selective = _selective_anchors(connection, anchors, response) if len(tokens) > 1 else []
            stages = [("all", all_terms)]
            if selective:
                stages.append(("anchored", '(' + ' OR '.join(selective) + ') AND (' + any_terms + ')'))
            stages.append(("any", any_terms))
            expressions = {}
            for mode, expression in stages:
                expressions.setdefault(expression, mode)
            for expression, mode in expressions.items():
                if len(response["results"]) >= limit or response["candidates_scanned"] >= candidate_limit:
                    break
                response["queries_used"].append(expression)
                if mode == "anchored":
                    response["warnings"].append("Explicit-phrase/acronym fallback used; these literal anchors are not verified legal scope.")
                elif mode == "any":
                    response["warnings"].append("Any-term fallback used; candidates may match only part of the question.")
                while len(response["results"]) < limit and response["candidates_scanned"] < candidate_limit:
                    # Excluding visited URLs lets a long document yield to other
                    # sources without scanning all of its matching pages in Python.
                    exclusion = " AND url NOT IN (" + ",".join("?" for _ in excluded) + ")" if excluded else ""
                    row = connection.execute(
                        "SELECT * FROM originals WHERE originals MATCH ?" + exclusion + " ORDER BY rank LIMIT 1",
                        [expression, *excluded],
                    ).fetchone()
                    if row is None:
                        break
                    response["candidates_scanned"] += 1
                    candidate = dict(row)
                    url = candidate.get("url")
                    if not isinstance(url, str) or not url:
                        errors.append("Indexed candidate has a missing or invalid URL")
                        break
                    excluded.append(url)
                    try:
                        candidate["pages_without_text"] = json.loads(candidate["pages_without_text"])
                        text = _verified_unit(root, objects, preserved, candidate, cache)
                        if candidate.get("text") != text:
                            raise ValueError("Indexed text differs from the canonical text unit")
                        excerpt = _excerpt(text, tokens)
                        if not excerpt:
                            raise ValueError("Matching canonical text unit is empty")
                        result = {key: candidate[key] for key in SOURCE_FIELDS}
                        result.update(research_id=_research_id(candidate), locator=candidate["locator"], excerpt=excerpt)
                        response["results"].append(result)
                    except (OSError, ValueError, KeyError, TypeError, RuntimeError) as exc:
                        errors.append(f"Indexed source {url}: {exc}")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, sqlite3.Error) as exc:
        errors.append(f"Research archive validation/search failed: {exc}")
    if response["candidates_scanned"] >= candidate_limit:
        response["warnings"].append("Candidate scan limit reached; additional sources may remain unexamined.")
    response["warnings"].extend(errors)
    response["status"] = "integrity-error" if errors else "ok" if response["results"] else "no-matches"
    return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()
    response = search_research_originals(args.root, args.query, args.limit)
    if response["status"] == "invalid-query":
        parser.error(response["warnings"][0])
    print(json.dumps(response, indent=2, ensure_ascii=True))
    return 1 if response["status"] in {"archive-unavailable", "integrity-error"} else 0


if __name__ == "__main__":
    raise SystemExit(main())
