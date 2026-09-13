# Evaluation Boundaries

## Public Checkout

The public edition must be evaluated separately from the larger local archive.
Missing source originals are intentional distribution exclusions, not evidence
that the omitted bytes can be treated as present. This edition does not inherit
the local corpus's exact-source eligibility or answer scores.

Portable regression tests use synthetic fixtures. Some integration tests require
the undistributed original-source archive; these are separately identified rather
than counted as public-edition passes. See `review/public-release-validation.json`
for the measured release run and exact selected test scope.

```sh
python -m pip install -r requirements-dev.txt
python -B scripts/build_search_index.py
python -B scripts/check_public_release.py
python -B scripts/check_public_release.py --staged
python -B scripts/test_public_release.py
```

The explicit `review/public-release-test-profile.json` identifies 12 archive-dependent
tests not selected for this edition. They remain in the source, not rewritten to
pass with missing evidence. Running unrestricted `unittest discover` against this
public edition will therefore also run those unavailable-archive assumptions and
is not expected to pass. Four public-distribution tests separately check event-chain
retrieval and the absence of source-based current-law approval. Platform skips are
reported independently from both passes and the 12 not-run tests.

Acquisition tests use synthetic permission records and mocked network responses.
They check scope, expiry, private-output boundaries and denial behavior, not real
publisher authorisation or legally valid use. Release checks inspect the current
tracked tree and exact staged blobs; they do not scan past commits, recall clones,
or prove that all apparently original prose is independently authored.

## Originating Local Diagnostic

On 13 September 2026, a targeted 12-question NEM battery diagnostic used separate
AI question/answer roles and a private gold set. Two fresh answering contexts used
frozen local evidence packets without internet access. The question designer then
adjudicated the answers. This was not independent professional certification or
an attested cross-model comparison.

- Ten questions were substantively complete and two partial.
- Across 36 required subquestions: 33 met, two partial, one unanswered.
- Including explicitly requested source support: nine complete questions.
- No affirmative material errors were identified in this small sample.
- The one question requiring a particular historical case missed that citation
  initially. Subsequent retrieval repair was a development result, not a new blind
  accuracy score.

The stage lacked the optional bulk originals archive and used operator-resolved
intake labels. These are material test conditions. The private gold, raw packets,
run logs and extracted-source quotations are not redistributed here; these local
results are reported provenance, not a publicly reproducible benchmark claim.

The local full-suite checkpoint had 447 passes and two Windows symlink-permission
skips. A later instruction-only change was followed by 109 passing workflow tests.
Those counts apply to the prior local environment, not automatically to this release.

## What Remains Unproven

Representative legal-answer accuracy, automatic natural-language intake, complete
source recall, production model integration, detection performance on real meetings,
expert outperformance and cost saving require further evaluation. No finite test
proves universal correctness. A correct conditional answer is not wrong merely
because evidence is absent, but material claims still need appropriate review,
and relevant real cases must be cited when they exist.
