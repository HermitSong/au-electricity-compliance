#!/usr/bin/env python3
"""Shared deterministic FTS search functions for the compliance KB."""

from __future__ import annotations

import json
import re
import sqlite3
from pathlib import Path


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does", "for",
    "from", "how", "i", "in", "is", "it", "of", "on", "or", "the", "to", "was",
    "were", "what", "when", "where", "which", "who", "why", "with", "would",
}


def tokenize(query: str) -> list[str]:
    tokens = re.findall(r"[A-Za-z0-9]+(?:[._/-][A-Za-z0-9]+)*", query.lower())
    useful = [token for token in tokens if token not in STOPWORDS and len(token) > 1]
    return useful[:40]


def fts_expression(query: str) -> str:
    tokens = tokenize(query)
    if not tokens:
        raise ValueError("Query has no searchable terms")
    escaped = [token.replace('"', '""') for token in tokens]
    clauses = [f'"{token}"' for token in escaped]
    if 1 < len(escaped) <= 12:
        clauses.insert(0, '"' + " ".join(escaped) + '"')
    return " OR ".join(clauses)


def applicable_as_of(row: dict, as_of: str | None) -> bool:
    if not as_of:
        return True
    if row["doc_type"] in {"enforcement-event", "technical-event"}:
        return not row["event_date"] or row["event_date"] <= as_of
    if row["doc_type"] in {"provision-version", "obligation-control"}:
        if row["effective_from"] and row["effective_from"] > as_of:
            return False
        if row["effective_to"] and row["effective_to"] < as_of:
            return False
    return True


def search(
    database: Path,
    query: str,
    *,
    jurisdiction: str | None = None,
    issue_family: str | None = None,
    doc_type: str | None = None,
    as_of: str | None = None,
    limit: int = 12,
    candidate_limit: int | None = None,
) -> list[dict]:
    expression = fts_expression(query)
    candidate_limit = candidate_limit or max(limit * 8, 80)
    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row
    try:
        where = ["documents_fts MATCH ?"]
        params: list[object] = [expression]
        if jurisdiction:
            where.append("lower(d.jurisdiction) LIKE ?")
            params.append(f"%{jurisdiction.lower()}%")
        if issue_family:
            where.append("(d.issue_family = ? OR d.issue_families_json LIKE ?)")
            params.extend((issue_family, f'%"{issue_family}"%'))
        if doc_type:
            where.append("d.doc_type = ?")
            params.append(doc_type)
        params.append(candidate_limit)
        rows = connection.execute(
            f"""SELECT d.*,
                bm25(documents_fts, 3.0, 1.0, 2.5, 2.5, 2.0) AS lexical_score
                FROM documents_fts
                JOIN documents d ON d.id = documents_fts.rowid
                WHERE {' AND '.join(where)}
                ORDER BY lexical_score ASC, d.authority_rank DESC
                LIMIT ?""",
            params,
        ).fetchall()
        results = []
        for raw in rows:
            row = dict(raw)
            if not applicable_as_of(row, as_of):
                continue
            row["issue_families"] = json.loads(row.pop("issue_families_json"))
            row["metadata"] = json.loads(row.pop("metadata_json"))
            row["retrieval_query"] = query
            row["retrieval_expression"] = expression
            results.append(row)
            if len(results) >= limit:
                break
        return results
    finally:
        connection.close()


def compact_result(row: dict) -> dict:
    metadata = row.get("metadata", {})
    source_chunk = metadata.get("source_text_chunk", {}) if isinstance(metadata, dict) else {}
    return {
        "evidence_id": row["evidence_id"],
        "doc_type": row["doc_type"],
        "title": row["title"],
        "entity": row["entity"],
        "jurisdiction": row["jurisdiction"],
        "event_date": row["event_date"],
        "status": row["status"],
        "coverage_status": row["coverage_status"],
        "issue_family": row["issue_family"],
        "temporal_classification": row["temporal_classification"],
        "current_mapping_status": row["current_mapping_status"],
        "effective_from": row["effective_from"],
        "effective_to": row["effective_to"],
        "official_url": row["official_url"],
        "related_official_url": row.get("related_official_url"),
        "source_path": row["source_path"],
        "sha256": row["sha256"],
        "source_locator": source_chunk.get("locator"),
        "source_text_sha256": source_chunk.get("text_sha256"),
        "source_snapshot_sha256": source_chunk.get("source_sha256"),
        "lexical_score": row.get("lexical_score"),
        "text": row["body"],
    }
