"""Dependency-free append-order policy shared by acquisition and research search."""


def select_manifest_rows(rows: list[dict]) -> tuple[dict, dict]:
    latest, preserved = {}, {}
    for row in rows:
        latest[row["canonical_url"]] = row
        if row.get("invalidates_prior_text"):
            preserved.pop(row["canonical_url"], None)
        if row.get("text_path") and row.get("extraction_status") != "blocked-or-error-page":
            preserved[row["canonical_url"]] = row
    return latest, preserved
