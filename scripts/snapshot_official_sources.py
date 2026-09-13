#!/usr/bin/env python3
"""Capture immutable byte snapshots of registered official HTTPS sources."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import mimetypes
from pathlib import Path
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from build_source_artifact_ledger import collect_canonical_urls


USER_AGENT = "AU-Power-Compliance-KB/1.0 source-preservation research contact=local-operator"
SAFE_HEADERS = {"content-type", "content-length", "etag", "last-modified", "cache-control"}


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_manifest(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8-sig").splitlines() if line.strip()]


def selected_urls(root: Path, scope: str, explicit_urls: list[str]) -> list[str]:
    if explicit_urls:
        return sorted(set(explicit_urls))
    if scope == "current-provisions":
        register = read_json(root / "data" / "provision-version-register.json")
        return sorted({item["official_url"] for item in register["provisions"] if item["status"] != "future-at-baseline"})
    references, _ = collect_canonical_urls(root)
    return sorted(references)


def response_headers(response) -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in response.headers.items()
        if key.lower() in SAFE_HEADERS
    }


def extension_for(url: str, content_type: str) -> str:
    content_type = content_type.split(";", 1)[0].strip().lower()
    known = {
        "application/pdf": ".pdf",
        "text/html": ".html",
        "application/xhtml+xml": ".html",
        "application/json": ".json",
        "text/plain": ".txt",
    }
    if content_type in known:
        return known[content_type]
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix and len(suffix) <= 8:
        return suffix
    return mimetypes.guess_extension(content_type) or ".bin"


def known_access_interstitial(data: bytes, content_type: str) -> bool:
    if 'html' not in content_type.lower():
        return False
    lowered = data.lower()
    return (b'<script' in lowered and b'triggerinterstitialchallenge' in lowered
            and b'/_sec/verify?provider=interstitial' in lowered)


def capture(url: str, output_root: Path, timeout: int, max_bytes: int, parent_url: str | None = None) -> dict:
    requested_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    base = {
        "capture_id": f"capture:{hashlib.sha256((url + requested_at).encode('utf-8')).hexdigest()[:24]}",
        "canonical_url": url,
        "requested_at": requested_at,
        "parent_canonical_url": parent_url,
    }
    if not url.startswith("https://"):
        return {**base, "capture_status": "failed", "error_type": "non-https-url", "error": "Only HTTPS sources may be captured."}
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,application/json,text/plain,*/*;q=0.5"})
    try:
        with urlopen(request, timeout=timeout) as response:
            headers = response_headers(response)
            declared = headers.get("content-length")
            if declared and int(declared) > max_bytes:
                raise ValueError(f"Declared content length {declared} exceeds limit {max_bytes}")
            data = response.read(max_bytes + 1)
            if len(data) > max_bytes:
                raise ValueError(f"Response exceeds byte limit {max_bytes}")
            final_url = response.geturl()
            if not final_url.startswith("https://"):
                raise ValueError("Redirect left HTTPS")
            digest = hashlib.sha256(data).hexdigest()
            content_type = headers.get("content-type", "application/octet-stream")
            extension = extension_for(final_url, content_type)
            relative = Path("official-snapshots") / digest[:2] / f"{digest}{extension}"
            destination = output_root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if not destination.exists():
                destination.write_bytes(data)
            result = {
                **base,
                "capture_status": "captured",
                "retrieved_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
                "response_url": final_url,
                "status_code": getattr(response, "status", 200),
                "response_headers": headers,
                "content_type": content_type,
                "size_bytes": len(data),
                "sha256": digest,
                "snapshot_path": relative.as_posix(),
            }
            if known_access_interstitial(data, content_type):
                result.update(capture_status='failed', error_type='html-access-interstitial',
                              error='HTTP 200 returned a known access challenge, not the requested source.',
                              artifact_use='rejected-response-bytes-for-audit-only')
            return result
    except HTTPError as exc:
        return {
            **base,
            "capture_status": "failed",
            "status_code": exc.code,
            "response_headers": response_headers(exc),
            "error_type": "http-error",
            "error": str(exc),
        }
    except (URLError, TimeoutError, ValueError, OSError) as exc:
        return {**base, "capture_status": "failed", "error_type": type(exc).__name__, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", choices=("current-provisions", "all-canonical"), default="current-provisions")
    parser.add_argument("--url", action="append", default=[])
    parser.add_argument("--parent-url")
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--max-mb", type=int, default=80)
    parser.add_argument("--delay", type=float, default=0.2)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = root / "official-snapshots" / "manifest.jsonl"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    prior = read_manifest(manifest_path)
    captured_urls = {row["canonical_url"] for row in prior if row.get("capture_status") == "captured"}
    urls = selected_urls(root, args.scope, args.url)
    attempts = []
    skipped = 0
    for index, url in enumerate(urls, 1):
        if url in captured_urls and not args.refresh:
            skipped += 1
            continue
        print(f"[{index}/{len(urls)}] {url}")
        result = capture(url, root, args.timeout, args.max_mb * 1024 * 1024, args.parent_url)
        attempts.append(result)
        if args.delay and index < len(urls):
            time.sleep(args.delay)
    if attempts:
        with manifest_path.open("a", encoding="utf-8", newline="\n") as handle:
            for row in attempts:
                handle.write(json.dumps(row, ensure_ascii=True, separators=(",", ":")) + "\n")
    all_rows = read_manifest(manifest_path)
    latest_by_url: dict[str, dict] = {}
    for row in all_rows:
        url = row["canonical_url"]
        if url not in latest_by_url or row["requested_at"] > latest_by_url[url]["requested_at"]:
            latest_by_url[url] = row
    successful_urls = {row["canonical_url"] for row in all_rows if row.get("capture_status") == "captured"}
    summary = {
        "scope": args.scope,
        "selected_url_count": len(urls),
        "attempted_count": len(attempts),
        "captured_count": sum(row["capture_status"] == "captured" for row in attempts),
        "failed_count": sum(row["capture_status"] == "failed" for row in attempts),
        "skipped_existing_count": skipped,
        "cumulative_attempt_count": len(all_rows),
        "cumulative_successful_url_count": len(successful_urls),
        "latest_failed_selected_url_count": sum(
            latest_by_url.get(url, {}).get("capture_status") == "failed" and url not in successful_urls
            for url in urls
        ),
        "manifest": manifest_path.relative_to(root).as_posix(),
    }
    (root / "data" / "source-capture-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
