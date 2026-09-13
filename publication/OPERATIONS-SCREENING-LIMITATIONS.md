# Operations Screening Limitations

**Date:** 10 September 2026

**Status:** documentation for a local research preview; not publication approval or enterprise validation.

Read the [operations screening guide](../OPERATIONS-SCREENING.md) for the input contract and local workflow, and the release claims and gates (local-only artifact; not distributed) before a demonstration, pilot or publication. Capability statements below define the bounded preview; verify them against the delivered implementation before release.

## Purpose and interpretation

The preview helps a reviewer find candidate issues in an authorised transcript and collect public-source research relevant to a supported category. Its inputs are a transcript text file (`.txt`), a context file (`.json`) and, optionally, an externally prepared AI-candidates file (`.json`). It does not record or transcribe a meeting.

**A candidate is a lead for review, never a final breach finding. A no-match result is never compliance clearance.** An empty result, a completed run, a citation, an accepted span or a passing diagnostic must not be used to close a matter, approve an action or conclude that no reporting obligation exists. A missing-input, unsupported-category or retrieval-failure result also provides no clearance.

A transcript records what was said or transcribed. It does not establish that an event occurred as described, that a speaker had authority, or that the account is complete. Reviewers need corroborating operational records and applicable sources before reaching a conclusion.

## Intrinsic epistemic and authority limits

These limits concern evidence and authority, not a claim that future AI engineering is impossible.

| Limit | Consequence for review |
|---|---|
| Unprovided hidden facts are not observable | The system cannot know an undisclosed event, exception, approval or policy merely from silence in the supplied material. An inference must remain an inference until supported. |
| A source hash records identity, not truth | Matching bytes do not establish authenticity of the underlying account, factual truth, legal applicability, completeness, currency or correct interpretation. |
| Finite tests do not prove universal correctness | Passing every tested fixture cannot establish correctness for every future transcript, jurisdiction, rule version or operating context. |
| A software result has no power to confer legal permission or privilege | A label, citation or reviewer button cannot itself authorise recording, retention, disclosure, customer action or a legal exception, or establish legal professional privilege. |

Better models, access and review can improve supported performance. They do not turn missing evidence into observed facts or a software output into an independent grant of authority.

## Missing enterprise prerequisites

These are deployment dependencies to establish and verify. Do not describe them as controls supplied by this preview.

- **Authorised, accurate source access:** approved access to relevant corporate records, policies, authoritative legal sources and later corrections; provenance, version dates, known gaps and a responsible source owner. Supplying a file does not prove its accuracy or the uploader's authority.
- **Recording and processing basis:** a documented review covering recording, transcription, the stated purpose, participants, relevant locations and any proposed external processing. Legal and privacy owners must resolve the applicable recording, use and disclosure conditions before real material enters a pilot.
- **Privacy-safe tenancy, access and retention:** an approved hosting or local-device arrangement with tested access separation, permissions, storage, logging, backups, retention and deletion, including applicable preservation requirements. Review provider terms and data handling separately for any external AI used to propose spans.
- **Company policy and applicability:** the entity, activity, jurisdiction, relevant date, contracts, internal policies, exceptions, approvals and responsible decision maker must be established from authorised records. Context JSON contains supplied assertions; it does not authenticate or resolve them.
- **Clock start and operational ownership:** a reviewer must establish the relevant event, awareness or other trigger and its evidenced time under the applicable rule and company process. Meeting time, file time and keyword detection time are not substitutes. An accountable owner must manage any real incident and deadline independently of this tool.
- **Privilege and legal review:** obtain a review of the intended recording, retention, sharing, access and legal-advice workflow. Neither a file label nor routing material through this preview establishes privilege or resolves a risk of waiver.

The OAIC recommends assessing privacy impacts and product suitability when selecting AI, and addressing privacy throughout its use. Its guidance also covers internal deployment and cautions that it does not address every relevant regulatory regime. Use it as an input to the organisation's review, not as an approval of this preview. [OAIC guidance on privacy and commercially available AI products](https://www.oaic.gov.au/privacy/privacy-guidance-for-organisations-and-government-agencies/guidance-on-privacy-and-the-use-of-commercially-available-ai-products).

The project gates above are proposed deployment requirements. This document does not determine which laws apply to a particular organisation or supply recording, retention or reporting thresholds.

## Present implementation limits

- Candidate discovery is lexical matching for supported categories, with optional import of external AI span proposals. Both can miss relevant issues and flag irrelevant statements. Negation, quotations, hypothetical plans, aliases, euphemisms, missing context, transcription errors and mixed-language material need explicit evaluation.
- There is no integrated audio recording, transcription service or LLM semantic reviewer. Accepting an AI-candidates JSON file does not mean the preview called a model, independently reviewed the proposal or validated its legal meaning. Preparing that file externally is a separate, authorised workflow.
- A valid category or matching text span shows a structural relationship to the input, not that the proposed issue is true, complete, material or legally applicable. External AI text is untrusted input; it cannot promote itself to a finding or override the retrieval boundary.
- Public research uses one fixed, non-personal question per supported category, passed to the existing `answer_kb.py` as an argument list. Raw transcript text, entity identifiers and imported candidate wording must not enter those queries. The query is selected from the category mapping, not composed from private meeting content.
- Category research is deliberately broad. Its results may omit controlling or contrary material and do not adjudicate the meeting facts. Existing retrieval, source-version, clause-binding and semantic-support limits remain relevant; multiple retrieval paths share dependencies.
- There are no autonomous operational actions or notifications. The preview does not send regulator or customer messages, create an incident-response service, enforce approvals or discharge an obligation by producing a report.
- Monthly research updates, where configured, are periodic public-source maintenance. They are not real-time incident monitors and do not detect every new event or manage incident deadlines.
- No operational detection accuracy, calibrated confidence, expert outperformance or cost reduction has been validated. Software and fixture diagnostics show behaviour on the exercised paths only.

These implementation limits can change through engineering and evaluation. Update the claims only after the change and its supporting evidence exist.

## Public and private data boundary

Maintain a **private corporate fact store separate from the public law and case store**. The private store holds meeting originals, transcripts, context, internal policies, entity mappings, imported proposals, reviewer decisions and generated screening outputs. Public-source material still needs a rights and privacy review before redistribution.

All screening outputs, including evidence packets, diagnostics containing input material and reviewer exports, must be outside the public KB and its publication tree. Keep private inputs outside that tree too. Do not ingest meeting content into public search indexes or use it as public retrieval queries. The approved public research question is the boundary between private screening and public-source retrieval, not an anonymised copy of the transcript.

An output-path check or argument-list invocation is a limited application control. It is not OS-level security, a tenant-isolation guarantee or universal anonymisation. Local files may still be exposed through permissions, synced folders, backups, logs, crash reports or other software. Names removed from a transcript do not prove that people or companies cannot be identified from context.

`.gitignore` is a convenience for avoiding some accidental additions. It does not protect tracked files, old commits, forced additions, downloadable archives, release assets or support uploads. A private output directory is not evidence that access and retention have been configured correctly.

Do not publicly upload corporate meeting recordings, transcripts, real pilot/test records, context files, AI proposals, outputs or support attachments. Debug through an approved private channel and share only the minimum authorised material. Public examples should be purpose-written synthetic fixtures, reviewed for personal information, secrets, source copying and resemblance to real incidents before release.

Collecting or preserving a raw original does not automatically license redistribution. The project's authored-content licence does not automatically cover official snapshots, third-party documents, recordings, transcripts or corporate records. Record asset-specific rights or distribute approved references instead.

Before each public commit or release, review the staged changes, tracked files and relevant history, plus generated downloads, source archives and release artifacts. Review issues, pull requests and support attachments before posting. Automated secret scans and fixture checks assist this review; passing them is not a privacy guarantee.

## Evaluation boundary

Parser, span-validation, category-routing, fixed-query, path and regression tests are **software/fixture diagnostics**. Even an expected candidate in every synthetic positive example is not a measured real-world recall rate. Citation presence, unchanged hashes and source retrieval are not expert agreement or legal-answer accuracy.

A meaningful pilot needs a declared workflow and population, independently adjudicated cases unseen during development, category-specific false positives and missed issues, uncertainty, reviewer workload and a matched baseline. Evaluate optional AI proposals separately from lexical-only screening. Agree sample size, acceptance criteria and stop conditions before observing results. Report failures and exclusions; do not turn a zero-error sample into universal assurance.

The minimum pilot gates and required evidence are maintained in Release Claims and Evidence Gates (local-only artifact; not distributed). A synthetic demonstration does not satisfy the gates for real corporate data or operational reliance.

## Ready-to-use bounded publication wording

Use the following only after the release gates are met and the released implementation matches it:

> This research preview screens authorised transcript text and supplied context for candidate compliance issues using lexical matching, with optional externally prepared AI span proposals. It retrieves public-source research through fixed category questions for human review. Candidates are not breach findings, and no match is not compliance clearance. There is no integrated transcription or LLM semantic reviewer, and no autonomous action or notification. Accuracy, expert outperformance and cost savings have not been validated. Corporate material and screening outputs belong in a separately controlled private store outside the public KB; local processing and path checks are not a security or anonymisation guarantee.

Publish this wording with links to the [operations guide](../OPERATIONS-SCREENING.md), this limitations document and the release gates (local-only artifact; not distributed). Any shorter announcement must retain the candidate/no-clearance distinction and link to the full limits.
