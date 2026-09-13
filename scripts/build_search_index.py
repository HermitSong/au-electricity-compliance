#!/usr/bin/env python3
"""Build the disposable SQLite FTS5 index from canonical repository records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return records


def digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def first_url(text: str) -> str | None:
    match = re.search(r"https://[^\s|)>;]+", text)
    return match.group(0).rstrip(".,") if match else None


def markdown_chunks(path: Path, root: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8-sig")
    relative = path.relative_to(root).as_posix()
    front_title = None
    title_match = re.search(r"(?m)^title:\s*(.+)$", text)
    if title_match:
        front_title = title_match.group(1).strip()
    sections: list[tuple[list[str], list[str]]] = []
    headings: list[str] = []
    body: list[str] = []

    def flush() -> None:
        nonlocal body
        content = "\n".join(body).strip()
        if content:
            sections.append((headings.copy(), body.copy()))
        body = []

    for line in text.splitlines():
        heading = re.match(r"^(#{1,4})\s+(.+?)\s*$", line)
        if heading:
            flush()
            level = len(heading.group(1))
            headings[:] = headings[: level - 1]
            while len(headings) < level - 1:
                headings.append("")
            headings.append(heading.group(2).strip())
        else:
            body.append(line)
    flush()

    chunks = []
    for index, (path_headings, lines) in enumerate(sections, 1):
        content = "\n".join(lines).strip()
        if not content or content == "---":
            continue
        title = " > ".join(item for item in path_headings if item) or front_title or path.stem
        # Keep tables and provision matrices intact where possible while bounding noisy context.
        pieces = [content[i : i + 7000] for i in range(0, len(content), 7000)]
        for piece_index, piece in enumerate(pieces, 1):
            suffix = f"-{piece_index}" if len(pieces) > 1 else ""
            chunks.append({
                "evidence_id": f"kb:{relative}#{index}{suffix}",
                "doc_type": "knowledge-chunk",
                "title": title,
                "body": piece,
                "entity": "",
                "instrument": "",
                "jurisdiction": "",
                "event_date": None,
                "publication_date": None,
                "status": "authored-knowledge",
                "source_family_id": None,
                "coverage_status": None,
                "issue_family": "",
                "issue_families": [],
                "temporal_classification": None,
                "current_mapping_status": None,
                "effective_from": None,
                "effective_to": None,
                "official_url": first_url(piece),
                "related_official_url": None,
                "source_path": relative,
                "authority_rank": 60,
                "metadata": {"heading_path": path_headings},
            })
    return chunks


def build_documents(root: Path) -> list[dict]:
    ledger = read_json(root / "data" / "source-coverage-ledger.json")
    coverage = {item["source_family_id"]: item for item in ledger["source_reviews"]}
    links = {item["event_id"]: item for item in read_jsonl(root / "data" / "event-provision-links.jsonl")}
    documents: list[dict] = []

    for filename, expected_type in (
        ("enforcement-events-full.jsonl", "enforcement-event"),
        ("technical-events-full.jsonl", "technical-event"),
    ):
        for event in read_jsonl(root / "data" / filename):
            link = links.get(event["event_id"])
            if link is None:
                raise ValueError(f"Missing temporal link for {event['event_id']}")
            review = coverage[event["source_family_id"]]
            body = "\n".join(
                f"{label}: {event[field]}"
                for label, field in (
                    ("Entity", "entity"), ("Issue", "issue"), ("Outcome", "outcome"),
                    ("Historical instrument or rule", "instrument_or_rule"),
                    ("Case status note", "case_status_note"),
                    ("Electricity relevance", "electricity_relevance"),
                )
            )
            documents.append({
                "evidence_id": f"event:{event['event_id']}",
                "doc_type": expected_type,
                "title": event["source_title"],
                "body": body,
                "entity": event["entity"],
                "instrument": event["instrument_or_rule"],
                "jurisdiction": event["jurisdiction"],
                "event_date": event["event_date"],
                "publication_date": event["publication_date"],
                "status": event["status"],
                "source_family_id": event["source_family_id"],
                "coverage_status": review["extraction_status"],
                "issue_family": link["issue_family"],
                "issue_families": link["issue_families"],
                "temporal_classification": link["temporal_classification"],
                "current_mapping_status": link["current_mapping_status"],
                "effective_from": None,
                "effective_to": None,
                "official_url": event["official_source_url"],
                "related_official_url": None,
                "source_path": f"data/{filename}",
                "authority_rank": 90 if expected_type == "enforcement-event" else 70,
                "metadata": {"event": event, "temporal_link": link},
            })

    provisions = read_json(root / "data" / "provision-version-register.json")
    for provision in provisions["provisions"]:
        body = "\n".join([
            f"Instrument: {provision['instrument']}",
            f"Provisions: {', '.join(provision['provisions'])}",
            f"Jurisdiction: {provision['jurisdiction']}",
            f"Status: {provision['status']}",
            f"Version note: {provision['version_note']}",
        ])
        documents.append({
            "evidence_id": f"provision:{provision['provision_id']}",
            "doc_type": "provision-version",
            "title": provision["instrument"],
            "body": body,
            "entity": "",
            "instrument": provision["instrument"] + " " + " ".join(provision["provisions"]),
            "jurisdiction": provision["jurisdiction"],
            "event_date": None,
            "publication_date": provisions["baseline_date"],
            "status": provision["status"],
            "source_family_id": None,
            "coverage_status": "reviewed-provision-register",
            "issue_family": provision["issue_family"],
            "issue_families": [provision["issue_family"]],
            "temporal_classification": "provision-version",
            "current_mapping_status": provision["status"],
            "effective_from": provision["valid_from"],
            "effective_to": provision["valid_to"],
            "official_url": provision["official_url"],
            "related_official_url": None,
            "source_path": "data/provision-version-register.json",
            "authority_rank": 100,
            "metadata": {"provision": provision},
        })

    obligation_register = read_json(root / "data" / "obligation-register.json")
    for obligation in obligation_register["obligations"]:
        applicability = obligation["applicability"]
        body = "\n".join([
            f"Instrument: {obligation['instrument']}",
            f"Provisions: {', '.join(obligation['provisions'])}",
            f"Jurisdiction: {obligation['jurisdiction']}",
            f"Actor class: {applicability['actor_class']}",
            f"Regulated activity: {applicability['regulated_activity']}",
            f"Control objective: {obligation['control_objective']}",
            f"Minimum control evidence: {', '.join(obligation['minimum_control_evidence'])}",
            f"Applicability rule: {applicability['decision_rule']}",
            f"Review status: {obligation['review_status']}",
        ])
        documents.append({
            "evidence_id": f"obligation:{obligation['obligation_id']}",
            "doc_type": "obligation-control",
            "title": f"{obligation['instrument']} control route",
            "body": body,
            "entity": applicability["actor_class"],
            "instrument": obligation["instrument"] + " " + " ".join(obligation["provisions"]),
            "jurisdiction": obligation["jurisdiction"],
            "event_date": None,
            "publication_date": obligation_register["baseline_date"],
            "status": obligation["review_status"],
            "source_family_id": None,
            "coverage_status": "machine-readable-obligation-register",
            "issue_family": obligation["issue_family"],
            "issue_families": [obligation["issue_family"]],
            "temporal_classification": "obligation-control-route",
            "current_mapping_status": obligation["authority_status"],
            "effective_from": obligation["valid_from"],
            "effective_to": obligation["valid_to"],
            "official_url": obligation["official_source"],
            "related_official_url": None,
            "source_path": "data/obligation-register.json",
            "authority_rank": 95,
            "metadata": {"obligation": obligation},
        })

    source_text_path = root / "data" / "source-text-chunks.jsonl"
    if source_text_path.exists():
        provisions_by_url: dict[str, list[dict]] = {}
        for provision in provisions["provisions"]:
            provisions_by_url.setdefault(provision["official_url"], []).append(provision)
        for chunk in read_jsonl(source_text_path):
            routing_urls = {chunk.get('parent_canonical_url'), chunk['canonical_url']} - {None}
            routed = [item for url in sorted(routing_urls) for item in provisions_by_url.get(url, [])]
            issue_families = sorted({item["issue_family"] for item in routed})
            jurisdictions = sorted({item["jurisdiction"] for item in routed})
            instruments = sorted({item["instrument"] for item in routed})
            documents.append({
                "evidence_id": f"source-span:{chunk['chunk_id']}",
                "doc_type": "official-source-span",
                "title": " | ".join(instruments) or "Captured official source",
                "body": chunk["text"],
                "entity": "",
                "instrument": " | ".join(instruments),
                "jurisdiction": " | ".join(jurisdictions),
                "event_date": None,
                "publication_date": chunk["retrieved_at"][:10],
                "status": "captured-official-source-text",
                "source_family_id": None,
                "coverage_status": "byte-hashed-source-snapshot",
                "issue_family": issue_families[0] if issue_families else "",
                "issue_families": issue_families,
                "temporal_classification": "official-source-snapshot",
                "current_mapping_status": None,
                "effective_from": None,
                "effective_to": None,
                "official_url": chunk["canonical_url"],
                "related_official_url": chunk.get("parent_canonical_url"),
                "source_path": chunk["snapshot_path"],
                "authority_rank": 110,
                "metadata": {"source_text_chunk": chunk},
            })

    source_register = read_json(root / "data" / "enforcement-source-register.json")
    for source in source_register["sources"]:
        review = coverage[source["id"]]
        body = "\n".join([
            f"Regulator: {source.get('regulator', '')}",
            f"Subject: {source.get('subject', '')}",
            f"Public record type: {source.get('public_record_type', '')}",
            f"Coverage: {source.get('coverage_start', '')} to {source.get('coverage_end', '')}",
            f"Extraction status: {review['extraction_status']}",
            f"Pages or years checked: {review['pages_or_years_checked']}",
            f"Gap periods: {', '.join(str(item) for item in review['gap_periods'])}",
            f"Gap reason: {review['gap_reason']}",
        ])
        documents.append({
            "evidence_id": f"source-family:{source['id']}",
            "doc_type": "source-family",
            "title": source["id"],
            "body": body,
            "entity": source.get("regulator", ""),
            "instrument": "",
            "jurisdiction": source["jurisdiction"],
            "event_date": None,
            "publication_date": review["checked_at"],
            "status": review["extraction_status"],
            "source_family_id": source["id"],
            "coverage_status": review["extraction_status"],
            "issue_family": source.get("subject", ""),
            "issue_families": [source.get("subject", "")],
            "temporal_classification": "coverage-record",
            "current_mapping_status": None,
            "effective_from": source.get("coverage_start"),
            "effective_to": source.get("coverage_end"),
            "official_url": source["url"],
            "related_official_url": None,
            "source_path": "data/enforcement-source-register.json",
            "authority_rank": 80,
            "metadata": {"source": source, "coverage_review": review},
        })

    for path in sorted((root / "knowledge-base").rglob("*.md")):
        documents.extend(markdown_chunks(path, root))
    return documents


def create_index(root: Path, output: Path) -> tuple[int, dict[str, int]]:
    documents = build_documents(root)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()
    connection = sqlite3.connect(output)
    try:
        connection.executescript(
            """
            PRAGMA journal_mode = WAL;
            CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE documents (
                id INTEGER PRIMARY KEY,
                evidence_id TEXT NOT NULL UNIQUE,
                doc_type TEXT NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL,
                entity TEXT NOT NULL,
                instrument TEXT NOT NULL,
                jurisdiction TEXT NOT NULL,
                event_date TEXT,
                publication_date TEXT,
                status TEXT NOT NULL,
                source_family_id TEXT,
                coverage_status TEXT,
                issue_family TEXT NOT NULL,
                issue_families_json TEXT NOT NULL,
                temporal_classification TEXT,
                current_mapping_status TEXT,
                effective_from TEXT,
                effective_to TEXT,
                official_url TEXT,
                related_official_url TEXT,
                source_path TEXT NOT NULL,
                authority_rank INTEGER NOT NULL,
                sha256 TEXT NOT NULL,
                metadata_json TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE documents_fts USING fts5(
                title, body, entity, instrument, issue_family,
                content='documents', content_rowid='id', tokenize='unicode61 remove_diacritics 2'
            );
            CREATE INDEX documents_type_idx ON documents(doc_type);
            CREATE INDEX documents_jurisdiction_idx ON documents(jurisdiction);
            CREATE INDEX documents_event_date_idx ON documents(event_date);
            CREATE INDEX documents_status_idx ON documents(status);
            CREATE INDEX documents_issue_idx ON documents(issue_family);
            """
        )
        counts: dict[str, int] = {}
        for item in documents:
            metadata_json = json.dumps(item["metadata"], ensure_ascii=True, sort_keys=True, separators=(",", ":"))
            sha = digest("\n".join((item["title"], item["body"], metadata_json)))
            cursor = connection.execute(
                """INSERT INTO documents (
                    evidence_id, doc_type, title, body, entity, instrument, jurisdiction,
                    event_date, publication_date, status, source_family_id, coverage_status,
                    issue_family, issue_families_json, temporal_classification,
                    current_mapping_status, effective_from, effective_to, official_url,
                    related_official_url, source_path, authority_rank, sha256, metadata_json
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    item["evidence_id"], item["doc_type"], item["title"], item["body"],
                    item["entity"], item["instrument"], item["jurisdiction"], item["event_date"],
                    item["publication_date"], item["status"], item["source_family_id"],
                    item["coverage_status"], item["issue_family"],
                    json.dumps(item["issue_families"], ensure_ascii=True),
                    item["temporal_classification"], item["current_mapping_status"],
                    item["effective_from"], item["effective_to"], item["official_url"],
                    item.get("related_official_url"), item["source_path"], item["authority_rank"], sha, metadata_json,
                ),
            )
            rowid = cursor.lastrowid
            connection.execute(
                "INSERT INTO documents_fts(rowid,title,body,entity,instrument,issue_family) VALUES(?,?,?,?,?,?)",
                (rowid, item["title"], item["body"], item["entity"], item["instrument"], item["issue_family"]),
            )
            counts[item["doc_type"]] = counts.get(item["doc_type"], 0) + 1
        connection.executemany("INSERT INTO meta(key,value) VALUES(?,?)", [
            ("schema_version", "1.0"),
            ("baseline_date", "2026-08-29"),
            ("canonical_root", str(root)),
            ("document_count", str(len(documents))),
        ])
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"SQLite integrity check failed: {integrity}")
        return len(documents), counts
    finally:
        connection.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = (args.output or root / "data" / "search-index.sqlite3").resolve()
    count, counts = create_index(root, output)
    print(json.dumps({"index": str(output), "documents": count, "by_type": counts}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
