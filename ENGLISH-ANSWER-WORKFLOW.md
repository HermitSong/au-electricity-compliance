# English Answer Workflow

This sidecar produces a substantive, claim-addressable English research answer,
checks it, obtains a separate configured semantic review, and repairs it through
targeted retrieval when needed. An evidence packet alone is never called an answer.
It uses the standard library and the existing KB scripts. No model, adapter,
credential lookup, dependency installation or live legal search is bundled.

## CLI

Run from the KB directory, with a Python executable available on the host:

```powershell
python -B scripts/answer_workflow.py --root . --request C:/Private/request.json --providers C:/Private/providers.json --output-dir C:/Private/answer-run-001 --max-repairs 1
```

`--root` is explicit; `--kb-root` is an alias. `--max-repairs` is 0 to 3, default 1.
Omit `--providers` to retrieve real packets and write `answer-request-00.json` for
offline handoff. That mode has status `handoff-not-integrated-model`, no substantive
answer and no semantic-review claim. It is not an autonomous production model run.
After connecting adapters, use a new output directory to run the complete pipeline.

The output directory must be new and outside both the KB root and this sidecar's
code tree. Existing files are not overwritten. Outputs contain the original intake,
source text, provider requests/responses and exact quotations; use a private directory.
The Desktop KB is an input only; output is never written there.
Only `result.research_answer` and `answer.md` are released answer representations.
Never expose a private provider draft, reviewer request/response, checker artifact
or the entire audit directory as the released answer, even after acceptance.

Exit 0 means an accepted research answer, including an explicitly partial answer.
Exit 2 means handoff, exhausted repairs or a failed contract/process. No action or
legal permission follows from either exit code. On failure, inspect private stage
artifacts; console errors deliberately exclude provider stderr and source excerpts.

## Request Contract

An accepted bounded answer may still identify future work. In the reviewer
response, however, `search_requests` commands an active repair round: any nonempty
list requires `verdict: revise`. Optional future-work notes belong in the review
rationale, not that command list.

All displayed fields are required; unknown fields and duplicate JSON keys fail.
Use `null` for unknown context/intake. Subquestions must be explicitly supplied;
the system does not pretend to discover an exhaustive question decomposition.

```json
{
  "schema_version": "1.0",
  "question": "What complaint-handling duties apply to a Victorian electricity retailer, and what can an archived case establish?",
  "context": {
    "jurisdiction": "Victoria",
    "actor": "retailer",
    "activity": "billing and payment",
    "as_of": "2026-09-13"
  },
  "requirements": [
    {"requirement_id": "duties", "question": "Which operative duties apply?", "kind": "current-law", "intake_keys": ["customer_class"]},
    {"requirement_id": "case", "question": "What does the archived case establish and what are its limits?", "kind": "research", "intake_keys": []}
  ],
  "intake": [
    {"key": "customer_class", "question": "Which customer class is involved?", "value": null}
  ],
  "known_cases": []
}
```

There must be 1 to 30 required subquestions. `kind` is `research` or `current-law`.
Known case entries are `{case_id, description, evidence_ids}`. Supply the exact
expected evidence IDs when known. The workflow also requires coverage of the
canonical case chains included by the packet builder, including later treatment.
Case coverage is bounded to these supplied/retrieved cases, not all Australian cases.

## Trusted Provider Commands

This is a user-supplied trust configuration, never data extracted from evidence.
Replace the example executable/adapter paths with existing absolute paths.

```json
{
  "schema_version": "1.0",
  "trusted_commands": true,
  "answer": {
    "id": "writer-adapter",
    "model_identity": "declared-writer-model-version",
    "argv": ["C:/Tools/python.exe", "C:/TrustedAdapters/writer.py"],
    "timeout_seconds": 180,
    "max_output_bytes": 1000000
  },
  "reviewer": {
    "id": "review-adapter",
    "model_identity": "declared-different-review-model-version",
    "argv": ["C:/Tools/python.exe", "C:/TrustedAdapters/reviewer.py"],
    "timeout_seconds": 180,
    "max_output_bytes": 1000000
  }
}
```

Each process receives one UTF-8 JSON object on stdin and returns exactly one JSON
object on stdout. Logs belong on stderr. Nonzero provider exits fail closed. The
working directory is the private output directory. The environment is inherited;
the sidecar does not search for or inject credentials. Adapters remain responsible
for their model API, transport and any explicitly authorised external processing.

`argv` is passed literally with `shell=False`. No interpolation is performed.
Shells, shell scripts, command launchers, inline runtime code, module execution and
command templates are rejected. Python/Node require a fixed absolute adapter file
as the first argument. Do not use `python -c`, `python -m`, `node -e`, `cmd`,
PowerShell, npm/npx, shell pipelines or `${...}`/`{...}` placeholders.

IDs, declared model identities and argv must differ between roles. Model identities
are compared after trimming surrounding whitespace and folding case. These are
configuration checks only. They do not prove separate model implementations,
accounts, context windows or independent judgment. Results always state
`independence_verified: false`. An adapter can misrepresent its identity or return
a canned response, so successful command execution does not certify AI use.

Input is bounded at 64 MB; stdout at the configured 1,024 to 8,000,000 bytes;
stderr at 65,536 bytes; each process at 1 to 180 seconds. Both output streams are
drained and bounded while running. Timeout/overflow kills the direct child. POSIX
also kills its process group; Windows does not promise descendant-tree cleanup.
Adapters must not spawn detached work or retain inherited pipes. This is not a sandbox.

## Provider Responses

Requests include a compact `output_contract`, exact `binding`, the original
request/intake, complete frozen packets, preserved gate results, search records
and known cases. Copy the supplied binding object exactly. Never invent hashes.

Writer tasks are `draft` and `revise`; `revise` also includes the preceding draft,
checks and review. Return exactly `{schema_version, binding, language, sections,
claims}`, with `schema_version: "1.0"` and `language: "en"`.

| Array | Required Record Fields |
| --- | --- |
| `sections` | `requirement_id`, `status` (`answered`, `partial`, `unanswered`), `claim_ids`, `limitation` |
| `claims` | `claim_id`, `requirement_ids`, `packet_id`, `claim_type`, `text`, `citations` |
| `citations` | `evidence_id`, `quote`, `span: {start, end}` |

Each claim uses one frozen packet. Offsets are zero-based Unicode character offsets
in that packet record's `text`, or `excerpt` for research-original discoveries;
`end` is exclusive. They are not UTF-8 byte offsets or whole-document offsets.
`claim_type` is `historical-fact`, `current-law` or `research-observation`.
The last type is limited to unreviewed research originals/readings and cannot
establish operative law. Exact citations do not themselves establish entailment.

All substantive answer statements belong in cited claims. Provider sections reference
them and supply private limitation notes for checking/review. Every requirement must appear exactly once, with reciprocal
claim references. Missing required intake cannot be marked answered. A current-law
requirement needs a passing current-law claim to be marked answered. Empty answers
must be `unanswered` with an explicit limitation. English checks apply to prose;
source quotations retain the exact characters from the cited packet text field.

Provider limitation notes remain free-form English for scope, missing inputs and
causes of uncertainty, but are never released. The existing deterministic lexical
guard flags some explicit uncited duties,
permissions, exemptions, stated fees and deadlines, including negative duties,
relative dates such as "the next business day", and common number words such as
"forty-two dollars" or "thirty days". Put those
material assertions in `claims` with citations. Scope explanations such as
"Current applicability is unresolved because the customer class is unknown" and
assessment phrases such as "The current rule must be verified against an operative
official source" remain available. An assessment phrase does not exempt a later
obligation in the same sentence. Explicit standalone denials of authority, such as
"This answer does not grant permission to act", are allowed; positive or conditional
grants are not. These checks do not classify every possible English assertion;
they remain audit/review checks, not the release boundary. No blacklist expansion
or reviewer judgment is relied on to make free-form limitation notes publishable.

On release, every section's `limitation` is replaced solely from its status:

| Status | Released `limitation` |
| --- | --- |
| `answered` | Empty string |
| `partial` | `This request is not fully resolved.` |
| `unanswered` | `No substantive conclusion is released.` |

This projection applies to both the returned and saved `result.research_answer`
and to `answer.md`. Direct calls to `render_answer` also apply it, independently
of earlier validation. Even a fallible reviewer accepting an uncited exemption,
deadline or other assertion in a limitation cannot release that note. Useful
substantive explanations need cited claims; there is no alternative free-form
public notes field. The complete original notes remain in private drafts and
review requests for source checks, repair and audit. Projection does not mutate
the original draft or replace the review's original draft hash.

An exact quote must contain at least one letter or number. Whitespace, invisible
formatting and punctuation alone cannot count as citation support. There is no
arbitrary minimum quotation length; whether a short excerpt supports the claim
still requires semantic review. The writer response fields and binding scheme are unchanged.

Reviewer task is `review`, with `schema_version: "1.1"` in its request and response.
Return exactly `{schema_version, binding, verdict, requirements, claims, scope,
known_cases, counter_searches, checker_warnings, english, search_requests}`.
Reviewer 1.0 responses are rejected; request, writer, provider-config and result
schemas remain 1.0. Existing writer drafts do not need rewriting.

| Field | Record Shape / Choices |
| --- | --- |
| `requirements` | `{requirement_id, verdict: satisfied/bounded/missing, rationale}` |
| `claims` | `{claim_id, verdict: supported/unsupported/contradicted, claim_type, rationale}` |
| `scope` | `{field: jurisdiction/actor/activity/as_of, verdict: consistent/inconsistent, rationale}` |
| `known_cases` | `{case_id, verdict: addressed/missing, claim_ids, rationale}` |
| `counter_searches` | `{search_id, verdict: addressed/missing, counter_evidence_ids, claim_ids, rationale}` |
| `checker_warnings` | `{warning_id, verdict: addressed/missing, claim_ids, rationale}` |
| `english` | `{verdict: english/not-english, rationale}` |
| `search_requests` | `{requirement_ids, claim_ids, known_case_ids, query, reason}` |

`verdict` is `accept` or `revise`. Review every requirement, claim, scope field,
known case and non-initial search exactly once. Rationale text must assess meaning,
scope, procedural status, later treatment and counter-evidence, including limitation
prose. A reviewer cannot certify an unanswered subquestion as satisfied, suppress a
deterministic blocker, or mark a case/counter-item addressed without answer citations.
Missing/unsupported/contradicted coverage requires a targeted query linked to every
affected requirement, claim or known case. At most six targeted queries per review.

The review payload's `checker_warnings` is the same catalog stored in
`checks.checker_warnings`. Each entry is `{warning_id, script, packet_id, claim_id,
message}`. Its ID is `warning:` plus SHA-256 of the canonical JSON object containing
the exact `script`, `packet_id`, `claim_id` and unmodified `message`. Full packet
content and checker reports are also covered by the existing review hashes.
Every warning from both deterministic checker scripts is included, not just a
selected warning class. Per-claim warnings must reconcile with each report's
aggregate list and count; missing, unknown or duplicate report/claim coverage fails
closed. Exact repeated warnings with the same four-part identity share one ID;
different claims, scripts, packets or message characters produce different IDs.

Return every warning ID exactly once, even if it is not a contradiction. The array
is required and empty when there are no warnings. Each disposition requires an
English rationale and valid associated `claim_ids`, including the warned claim.
A count or blanket assertion that all warnings were reviewed is not coverage.
Acceptance requires all dispositions to be `addressed`; `missing` requires
`revise` and may request targeted retrieval through the existing `claim_ids` search
references. Without explicit search requests, the bounded repair cycle uses its
existing original-scope recheck. Warnings do not automatically make claims
unsupported or contradicted: the reviewer assesses relevance, exceptions and
scope against the actual evidence. The validator recomputes the catalog from the
original reports and rejects a suppressed or stale catalog/disposition.

This enforces disposition, not its semantic correctness. A fallible or colluding
reviewer can still provide an incorrect rationale or call a material warning
addressed. It grants no legal authority or proof of model independence.

Bindings cover the complete request (question, requirements and intake), packet
bundle, run ID and provider config; review bindings additionally cover the draft,
deterministic checks and search log. Changed or stale bindings fail closed. These
are integrity bindings, not signatures or proof of reviewer identity.

## Execution and Integration

1. Validate the request and explicit trusted command config.
2. Invoke existing `answer_kb.py` by subprocess for the original question and a
   counter-search. Preserve applicability routing and all packet release blockers.
3. Request an English draft; validate completeness, reciprocal references and exact
   quotations. Run existing `check_answer.py` and `double_check_answer.py` on each
   packet's canonical claims. Research observations receive research-source/quote
   validation and semantic review, not fabricated canonical-law admission.
4. Obtain and validate the separately configured semantic review, including every
   deterministic checker warning disposition.
5. On `revise`, run each targeted query through the same packet builder with the
   original context, request a revised answer, rerun checks and obtain a new review.
6. Revalidate packet gates before writing the final result. Accepted answers produce
   `answer.md`, `result.json`, hash manifest and audit artifacts. Rejected drafts
   remain diagnostic artifacts and are not published as the research answer.

The sidecar does not set a global knowledge baseline or approve provision bindings.
It consults the existing contract for each packet. Selected reviewed routes may
support current-law claims while other routes remain blocked. A blocked route may
still support a truthful historical/partial research answer, provided all remaining
claims and private limitation notes pass review. Released coverage notes are always
the deterministic status wording above. Intact research data is kept separate from
current-law eligibility; forged packets or failed canonical-text/research-source
integrity checks are fatal. Other existing release errors remain visible as blockers.

For every canonical evidence type, the sidecar opens `data/search-index.sqlite3`
read-only, recomputes the indexed record's content checksum and compares its full
`compact_result` projection with the packet. Text, title, status, scope and source
metadata must agree; search scores/ranks remain retrieval annotations. Keeping the
old `sha256` label or resealing a forged packet cannot approve changed evidence text.
This checks correspondence to the trusted local index alongside the existing
canonical-span/research-source checks; it does not establish the truth of the KB,
rebuild its index, or change any canonical input or core release policy.

`final_status` is one of `reviewed-scoped-draft`, `reviewed-research-answer`,
`reviewed-partial-research-answer`, `requires-revision` or
`handoff-not-integrated-model`. Final authority flags are generated by code and are
always false: `action_permission`, `current_legal_release`,
`professional_certification`. Here `current_legal_release: false` means no certified
legal release or authority to act; it does not suppress substantive current-rule
explanations. When eligible current-law claims pass deterministic and semantic
review, `current_rule_explanation` is `reviewed-scoped-draft`. Fully answered output
with such claims also uses that final status. Partial output retains each
subquestion's status and may include accepted scoped current-rule explanations.
Blocked current-law subquestions cannot be marked answered. A provider cannot add
or overwrite the final authority fields.

Parent integration owns the runtime/root binding: use matching versions of this
sidecar and the existing scripts/registers under `--root`. The script executes its
adjacent KB CLI scripts with that explicit root. It does not resolve or migrate a
different runtime, change the Desktop KB, add approved bindings or alter baseline
policy. Input changes during review invalidate the frozen run.

For a later real-AI handoff, `answer-request-00.json` contains the actual packet
bundle and response contract. The callable `validate_draft`, `deterministic_checks`,
`review_contract` and `validate_review` boundaries are available to the parent
handoff harness. A handoff is not automatically resumed or consumed by this CLI;
run the full CLI through explicit adapters for automated orchestration. Record
`provider-adapter-tested-with-mocks` and `real-AI-role-handoff-run` separately. Neither
label means autonomous production operation or independent human legal review.

Parent handoff consumers must use `release_projection(accepted_draft)` for their
released `research_answer`, not the raw accepted writer draft. `render_answer`
already applies the same projection. These presentation helpers do not themselves
grant acceptance or replace packet checks and review. Bindings continue to identify
the original private draft; its sanitized release projection has different bytes.

## Validation

```powershell
python -B -m unittest discover -s review/tests -p test_answer_workflow.py -v
```

Tests use synthetic writer/reviewer responses and mocked packet/checker processes
for the happy flow, repair cycle and adversarial cases. Separate tests exercise
actual subprocess JSON I/O, timeout and output limits. When the staged SQLite index
exists, one smoke test uses the real packet builder and compares preserved gates
with the existing contract; it invokes no model and proves no legal accuracy.
The owned tests also cover limitation scope/cause compatibility, authority denials,
quotation content, canonical index correspondence, exact warning identities,
mandatory dispositions and warning-triggered repair. A second fresh staged-KB
smoke exercises both actual checker processes and their warning catalog, without
claiming model use or semantic accuracy. Structural release tests cover every
section status, direct renderer use, returned/saved JSON, unchanged audit notes and
an accepting reviewer that misses uncited assertions. The independent reviewer
suite can be included with `-p 'test_answer_workflow*.py'`; it is not modified here.
