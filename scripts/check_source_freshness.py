#!/usr/bin/env python3
"""Report freshness and extractability of current provision sources."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--as-of", default=date.today().isoformat())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    as_of = datetime.fromisoformat(args.as_of).replace(tzinfo=timezone.utc)
    policy = read_json(root / "data" / "source-refresh-policy.json")
    register = read_json(root / "data" / "provision-version-register.json")
    captures = read_jsonl(root / "official-snapshots" / "manifest.jsonl")
    chunks = read_jsonl(root / "data" / "source-text-chunks.jsonl")
    extracted_urls = {row["canonical_url"] for row in chunks}
    latest_success: dict[str, dict] = {}
    latest_attempt: dict[str, dict] = {}
    for row in captures:
        url = row["canonical_url"]
        if url not in latest_attempt or row["requested_at"] > latest_attempt[url]["requested_at"]:
            latest_attempt[url] = row
        if row.get("capture_status") == "captured" and (
            url not in latest_success or row["retrieved_at"] > latest_success[url]["retrieved_at"]
        ):
            latest_success[url] = row

    rows = []
    for provision in register["provisions"]:
        if provision["status"] == "future-at-baseline":
            continue
        url = provision["official_url"]
        capture = latest_success.get(url)
        max_age = (
            policy["current_provision_max_age_days"]
            if provision["status"] in {"current-at-baseline", "current-at-baseline-appellate-control"}
            else policy["route_only_source_max_age_days"]
        )
        age_days = None
        reasons = []
        if capture:
            age_days = (as_of - parse_timestamp(capture["retrieved_at"])).total_seconds() / 86400
            if age_days > max_age:
                reasons.append(f"Snapshot is older than the {max_age}-day policy.")
        else:
            attempt = latest_attempt.get(url)
            reasons.append("No successful immutable snapshot is available.")
            if attempt and attempt.get("capture_status") == "failed":
                reasons.append(f"Latest capture failed: {attempt.get('error_type')} {attempt.get('status_code') or ''}".strip())
        if url not in extracted_urls:
            reasons.append("No addressable text was extracted from the official snapshot.")
        rows.append({
            "provision_id": provision["provision_id"],
            "authority_status": provision["status"],
            "official_url": url,
            "max_age_days": max_age,
            "snapshot_retrieved_at": capture.get("retrieved_at") if capture else None,
            "snapshot_age_days": round(age_days, 3) if age_days is not None else None,
            "addressable_text_available": url in extracted_urls,
            "freshness_status": "fresh-and-addressable" if not reasons else "blocked",
            "reasons": reasons,
        })
    blocking_current = [
        row for row in rows
        if row["authority_status"] in {"current-at-baseline", "current-at-baseline-appellate-control"}
        and row["freshness_status"] == "blocked"
    ]
    report = {
        "schema_version": "1.0",
        "as_of": args.as_of,
        "provision_source_count": len(rows),
        "fresh_and_addressable_count": sum(row["freshness_status"] == "fresh-and-addressable" for row in rows),
        "blocked_count": sum(row["freshness_status"] == "blocked" for row in rows),
        "blocking_current_provision_count": len(blocking_current),
        "release_status": "blocked-current-source-gaps" if blocking_current else "current-source-gate-passed",
        "sources": rows,
    }
    output = args.output or root / "data" / "source-freshness-report.json"
    output.write_text(json.dumps(report, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "sources"}, indent=2, ensure_ascii=True))
    return 0 if not blocking_current else 2


if __name__ == "__main__":
    raise SystemExit(main())
