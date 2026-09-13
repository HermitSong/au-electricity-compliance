# Public Structured Data

This directory contains source-linked public-event metadata, temporal routing,
source coverage and historical review records. See `public-release-profile.json`
and the root `DISTRIBUTION.md` for the public projection.

There are 824 enforcement/compliance records, 50 technical events, 54 source
families and 40 provision routes. Record count is not a count of proven breaches
or independent cases, and collection completeness is not established.

The original 34 provision routes retain their review limitations. Six later routes
have historical scoped AI review receipts, but the required official bytes and
extracted spans are not distributed here. No current-law approval follows from
the receipt alone. Earlier statements that four Victorian retail page ranges were
approved were superseded by the stricter exact-clause review controls.

`source-artifact-ledger.jsonl` describes the originating local archive, not files
bundled in the public edition. `source-text-chunks.jsonl` and SQLite indexes are
local-only build/acquisition outputs. Build the index from the root using
`python -B scripts/build_search_index.py`; a larger local index count from an older
research report is not the public-edition count.

Automatic event-to-provision links remain candidates unless specifically reviewed.
Dates, jurisdiction, conduct period, source version and subsequent treatment must
be considered together. Historical case retrieval does not approve an action.
