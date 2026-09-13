#!/usr/bin/env python3
"""Build deterministic provision-to-official-text bindings and explicit gaps."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from reviewed_bindings import reviewed_binding


ERCP_PARENT_URL = (
    "https://www.esc.vic.gov.au/electricity-and-gas/codes-guidelines-and-policies/"
    "energy-retail-code-practice"
)

CANDIDATE_PAGE_RANGES = {
    "VIC-ERCP-V6-PAYMENT-DIFFICULTY-2026-08-29": (98, 110, "Part 6, clauses 121-146"),
    "VIC-ERCP-V6-FAMILY-VIOLENCE-2026-08-29": (110, 113, "Part 7, clauses 147-160"),
    "VIC-ERCP-V6-LIFE-SUPPORT-2026-08-29": (113, 128, "Part 8, clauses 161-174"),
    "VIC-ERCP-V6-DISCONNECTION-2026-08-29": (131, 139, "Part 10, clauses 179-193"),
}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def matching_chunks(chunks: list[dict], official_url: str) -> list[dict]:
    return [
        chunk for chunk in chunks
        if chunk["canonical_url"] == official_url or chunk.get("parent_canonical_url") == official_url
    ]


def build(root: Path) -> dict:
    register = read_json(root / "data" / "provision-version-register.json")
    chunks = read_jsonl(root / "data" / "source-text-chunks.jsonl")
    bindings = []
    for provision in register["provisions"]:
        approved = reviewed_binding(root, provision, chunks)
        if approved is not None:
            bindings.append(approved)
            continue
        provision_id = provision["provision_id"]
        candidates = matching_chunks(chunks, provision["official_url"])
        candidate = CANDIDATE_PAGE_RANGES.get(provision_id)
        if candidate:
            first_page, last_page, clause_scope = candidate
            selected = [
                chunk for chunk in candidates
                if chunk.get("parent_canonical_url") == ERCP_PARENT_URL
                and chunk["locator"].startswith("page:")
                and first_page <= int(chunk["locator"].split(":", 1)[1]) <= last_page
            ]
            expected_pages = set(range(first_page, last_page + 1))
            found_pages = {int(chunk["locator"].split(":", 1)[1]) for chunk in selected}
            complete = found_pages == expected_pages
            status = "candidate-page-range-located" if complete else "candidate-range-incomplete"
            review_status = "needs-pinned-version-and-exact-clause-review" if complete else "blocked-missing-source-pages"
            supports_drafting = False
        else:
            selected = []
            clause_scope = None
            if provision["status"] == "future-at-baseline":
                status = "future-not-operative"
                review_status = "not-applicable-at-baseline"
            elif not candidates:
                status = "official-text-unavailable"
                review_status = "blocked-no-addressable-source-text"
            else:
                status = "instrument-text-captured-exact-clause-unverified"
                review_status = "needs-clause-level-binding"
            supports_drafting = False
        bindings.append({
            "provision_id": provision_id,
            "authority_status": provision["status"],
            "official_url": provision["official_url"],
            "clause_scope": clause_scope,
            "binding_status": status,
            "review_status": review_status,
            "supports_current_law_drafting": supports_drafting,
            "supports_operational_execution": False,
            "professional_legal_review_status": "required-before-execution",
            "source_span_ids": [f"source-span:{chunk['chunk_id']}" for chunk in selected],
            "source_locators": [chunk["locator"] for chunk in selected],
            "source_sha256_values": sorted({chunk["source_sha256"] for chunk in selected}),
            "limitation": (
                "The binding proves the location and integrity of the captured clause range. "
                "It does not decide factual applicability, statutory interactions, exceptions or legal advice."
                if supports_drafting else
                "The route is not bound to an exact operative clause range and must fail closed for current-law drafting."
            ),
        })
    counts = Counter(item["binding_status"] for item in bindings)
    return {
        "schema_version": "1.0",
        "baseline_date": register["baseline_date"],
        "purpose": "Bind provision routes to immutable, addressable official text without treating instrument-level capture as clause-level proof.",
        "release_rule": "Current-law drafting requires supports_current_law_drafting=true for every controlling provision. Execution always requires separate accountable approval.",
        "binding_count": len(bindings),
        "binding_status_counts": dict(sorted(counts.items())),
        "bindings": bindings,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output or root / "data" / "provision-source-bindings.json"
    data = build(root)
    output.write_text(json.dumps(data, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Wrote {data['binding_count']} provision-source bindings to {output}")
    print(json.dumps(data["binding_status_counts"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
