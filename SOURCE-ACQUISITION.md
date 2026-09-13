# Private Source Acquisition

The public edition distributes original tooling, curated knowledge and source
references, not a ready-made official-text archive. Use the
[source-acquisition skill](skills/au-lawful-source-acquisition/SKILL.md) to assemble
the relevant evidence privately. This workflow reduces accidental redistribution;
it is not a guarantee of lawful acquisition or use.

## Permission Record

Keep `permissions.local.json` outside all Git worktrees. An empty starting record
is valid but authorises no source:

```json
{"schema_version": "1.0", "permissions": []}
```

Each reviewed entry needs these fields. The program checks structure, exact URL
scope and the UTC date interval, not whether the claimed permission is legally
valid or the reviewer is entitled to grant it.

| Field | Required meaning |
| --- | --- |
| `id` | Local permission-record identifier |
| `urls` | Nonempty list of exact public HTTPS URLs; no host wildcards |
| `purpose` | Actual intended collection and local-use purpose |
| `basis_type` | `publisher-licence`, `written-permission` or `reviewed-statutory-exception` |
| `basis_reference` | Publisher policy URL or private written advice/permission reference |
| `reviewed_by` | Actual accountable reviewer; not an invented identity |
| `reviewed_on` | Actual review date, `YYYY-MM-DD` |
| `valid_until` | Review/permission expiry date, `YYYY-MM-DD` |
| `actions` | Exactly `download`, `local-store`, `extract-text` |
| `access_review` | `automated-access-permitted`, after reviewing access terms |
| `privacy_review` | `no-personal-information-expected` or `reviewed-lawful-handling` |

An applicable grant or reviewed exception must cover the actual material,
third-party components, copying and intended use. Include only URLs genuinely
within that scope. The collector supports this single combined operation; sources
permitted only for reading or metadata use remain reference-only. Expiry stops
new downloads, not automatic deletion of already-held files; independently review
retention and any continuing-use conditions. A timestamp or approval checkbox does
not create rights. Keep supporting private correspondence out of the public repo.

## Commands

From the checkout root, first inventory without network access:

```sh
python -B scripts/collect_source_originals.py --output-root ../au-electricity-private --inventory-only
```

After actual permissions and operator approval, use an explicit bounded download:

```sh
python -B scripts/collect_source_originals.py --output-root ../au-electricity-private --download --permissions ../au-electricity-private/permissions.local.json --max-requests 20 --workers 1
```

Without `--download`, no network requests are made. Without a permission record,
download mode fails before network access. Unapproved/expired URLs remain in the
inventory with an acquisition-permission gap. Newly discovered attachments need
their own recorded URL permissions. Automatic redirects are disabled, including
same-origin redirects. Review the replacement URL and acquire it directly under
its own permission record and robots policy. A publisher-wide licence can support a reviewed URL cohort,
but does not make every item on the publisher's site eligible.

The transport does not use browser profiles or credentials. It checks robots.txt,
request budgets and host delays separately from copyright/local-use permissions.
`--max-requests` counts source URL attempts, not individual HTTP dispatches; a
cached robots check is additional for each host. Redirects add no hidden requests.
401, 403 and 429 responses pause that host. Check recorded denials before retrying;
robots allowance, absence or a successful HTTP response is not a licence.

`collect_enumerated_sources.py` and `collect_observed_attachments.py` also require
`--permissions` for their specialised cohorts and use the same transport gate.
`snapshot_official_sources.py` and `recover_browser_sources.cjs` no longer perform
network acquisition. Historical commands referencing them describe old runs.
Manual browser capture and offline import/OCR helpers are separately reviewed
operations, not automatic fallbacks around a denial. Check rights and private
output paths before invoking those helpers.

## Evidence and Accuracy

The collector writes content-addressed HTTP bytes, separate extracted objects,
permission-record hashes and an append-only acquisition manifest under the private
output root. Privacy-sensitive provenance stays private. No source is automatically
added to the public knowledge files or approved for current-law answers.

The standalone original-search/read commands accept the private archive root.
The answer workflow does not automatically merge this separate archive into the
public checkout's controlled evidence index. Review and admission into a private
working knowledge copy remain explicit operator steps, not a completed integration.

Inventory mode can also rebuild the private research index after interruption.
Re-extraction needs renewed applicable permissions. Do not modify source bytes to
make a test pass. Review pages, OCR, version/commencement, jurisdiction, exceptions,
case status and later treatment before making exact clause bindings. See
`CLAUSE-REVIEW.md`, `ORIGINAL-READING.md` and `ANSWER-WORKFLOW.md`.

Corpus backfill and question-scoped research are complementary. More files are
not automatically more accurate; irrelevant or outdated records can confuse
retrieval. Never claim that downloading every known URL establishes all-Australia
coverage, professional-level performance or zero legal risk. Keep the source gaps
and the public/private evaluation conditions visible.

## Rights References

Checked on 13 September 2026; consult current terms and source-specific notices:

- [Australian copyright-user guidance](https://www.ag.gov.au/rights-and-protections/copyright/copyright-users)
- [OAIC statement on publicly accessible data scraping](https://www.oaic.gov.au/news/media-centre/global-expectations-of-social-media-platforms-and-other-sites-to-safeguard-against-unlawful-data-scraping)

This is a technical workflow with operator-controlled records, not independent
copyright, privacy or professional legal certification. The project's
source-available licence does not grant any rights over third-party sources.
