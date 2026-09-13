# Accuracy-First Knowledge Architecture

**Decision date:** 29 August 2026  
**System name:** Temporal Evidence Graph with Hybrid Retrieval  
**Priority:** legal and factual accuracy before latency or token cost

## Architecture decision

The repository was previously a Markdown and JSON evidence corpus with a routing skill and evaluation files. It was not a runtime RAG or KAG system because it had no searchable index, retrieval service, authority graph, answer evidence packet or independent answer validator.

The target is not plain vector RAG and not an LLM-generated knowledge graph as the source of truth. It is a temporal evidence system with four separate layers:

1. **Canonical evidence layer.** Official event records, byte-hashed source snapshots, explicit remote-only provenance gaps, source-family coverage, provision versions, provision-to-source bindings, obligations and procedural status are authoritative. Generated summaries, embeddings and graph edges may never overwrite this layer.
2. **Derived retrieval layer.** SQLite FTS5 supplies exact entity, clause, date and phrase retrieval. A production deployment may add dense embeddings. Results from independent retrievers are merged with reciprocal rank fusion.
3. **Temporal authority layer.** Event-to-provision links record what applied at the event date, the current comparator, supersession, appeal status and unresolved version checks.
4. **Answer and verification layer.** An answer is drafted only from a frozen evidence packet. Every material claim must cite evidence. A deterministic checker and an independent second search test citations, current-law support, procedural status, jurisdiction and known public-source gaps.

This design may use GraphRAG, KAG or LightRAG as an optional derived discovery index. None of them is permitted to create controlling legal facts without an official source and a reviewed canonical record.

## Why not plain RAG

Vector similarity is useful for paraphrases but weak for exact rule numbers, similarly named entities, state/national boundaries, procedural status and questions asking what law applied on a past date. A highly relevant old case can still be legally wrong for a current-law answer. Lexical, metadata and temporal checks therefore run before generation.

## Why not adopt GraphRAG as the legal backend

Microsoft describes GraphRAG as an LLM-based pipeline for extracting structured data from unstructured text. Its repository also says that it is a research project, is largely in maintenance mode, is not an officially supported Microsoft offering, can be expensive to index and normally requires prompt tuning. It remains useful for broad thematic discovery, but generated entity and relationship extraction is not a sufficiently controlled legal source of truth.

Source: https://github.com/microsoft/graphrag (retrieved 2026-08-29).

## Why not adopt KAG as the whole system

OpenSPG KAG combines schema-constrained knowledge construction, knowledge/chunk mutual indexing and logical-form-guided hybrid reasoning. Those are strong ideas for multi-hop professional-domain questions. The platform is substantially heavier than this repository requires, and its extracted graph still depends on model output. The repository adopts the useful concepts, especially schema constraints and mixed exact/text/graph operations, without delegating legal validity to the generated graph.

Source: https://github.com/OpenSPG/KAG (retrieved 2026-08-29).

## LightRAG role

LightRAG provides graph and vector retrieval, incremental updates and multiple query modes. Its own documentation says that graph extraction requires an LLM and that query models process long, noisy contexts. It can be trialled as a discovery index after the deterministic baseline passes evaluation. Its graph, vector store and cache remain disposable derived data.

Source: https://github.com/HKUDS/LightRAG (retrieved 2026-08-29).

## Retrieval sequence

1. Parse the question into jurisdiction, actor, event/current date, issue families, requested legal status and exact terms.
2. Fail closed with `needs-applicability-input` when jurisdiction, actor, activity or answer date can change the applicable regime.
3. Run Search A against SQLite FTS5 using exact names, phrases, rule numbers and metadata filters.
4. Run Search B independently against canonical JSON and Markdown using a separate in-memory token and phrase scorer.
5. Merge ranks with reciprocal rank fusion. Preserve the rank and query provenance of every hit.
6. Traverse approved temporal links. Keep deterministic keyword links quarantined as `candidate-auto-mapped` until independent review.
7. Bind every controlling provision to an exact addressable clause range. Instrument-level capture without an exact binding remains `needs-live-verification`.
8. Build a content-addressed evidence packet containing exact text, document type, jurisdiction, effective dates, status, official URL, source-artifact status, addressable official-source spans and canonical-register checksums.
9. Draft only from that packet. Cite every material factual or legal claim by evidence ID, including a source span bound to each current provision.
10. Run deterministic checks and an independent reviewer search. Fail closed when current-law support, official evidence, status or coverage is unresolved.

Elasticsearch documents reciprocal rank fusion as a method for combining result sets with different relevance indicators without requiring comparable raw scores. The local implementation applies the same rank formula to two FTS query formulations; a production deployment can add a dense retriever as a third list.

Source: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion (retrieved 2026-08-29).

## Temporal and authority rules

- `event_date` determines the historical rule comparison date.
- `valid_from` and `valid_to` determine whether a provision version may support a current-law claim.
- A future commencement cannot support an answer as current law.
- A paid infringement or penalty notice is not converted into a court admission.
- Proceedings and allegations cannot support a final-liability claim.
- A technical report cannot support a contravention claim unless an official decision separately makes that finding.
- A first-instance outcome that was quashed or overturned cannot support the displaced proposition.
- The latest in-force text and latest final controlling appellate judgment take priority for present guidance.
- A historical case remains searchable and is linked to its current comparator; it is never silently rewritten.

## Fail-closed answer contract

The answer stage returns one of:

- `ready-for-grounded-drafting`: official evidence, an applicable provision version and its verified clause-level source binding are present;
- `historical-only`: the packet supports the historical position but not a current-law conclusion;
- `needs-live-verification`: a current rule, guideline, penalty value or transition has not been verified at the answer date;
- `coverage-gap`: a registered public source family relevant to the question has an unresolved archive gap;
- `insufficient-evidence`: no adequate official evidence was retrieved; or
- `procedural-status-conflict`: the proposed language exceeds the legal status of the source.
- `needs-applicability-input`: a material jurisdiction, actor or activity is unresolved, so retrieval is not run by default.

No amount of model confidence overrides these states.

## Double check

The deterministic checker validates evidence IDs, HTTPS official URLs, hashes, dates, jurisdiction, current-version eligibility and status-compatible language. A separate answer auditor then repeats retrieval from the question and checks each sentence against the cited span. The same model may not act as both sole answerer and sole auditor in a production approval path.

RAGChecker uses claim-level entailment and separates retriever and generator diagnostics. Ragas similarly measures whether response claims are supported by retrieved context. These are useful diagnostics, but legal acceptance also requires deterministic provision-version, jurisdiction, status and coverage tests that an LLM judge cannot waive.

Sources: https://github.com/amazon-science/RAGChecker and https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/ (retrieved 2026-08-29).

## Acceptance metrics

| Metric | Required interpretation |
|---|---|
| Citation existence | 100% of material claims cite an indexed evidence ID. |
| Official-source rate | 100% of controlling legal and enforcement claims use official evidence. |
| Provision-version accuracy | 100% on the reviewed temporal test set. |
| Jurisdiction routing | 100% on state/national conflict questions. |
| Procedural-status accuracy | 100% on proceedings, notices, appeals and technical reports. |
| Historical-conflict detection | 100% on known old-rule and quashed-case tests. |
| Citation entailment | Every cited span supports the claim; automated scores require human sampling. |
| Abstention correctness | The system refuses current-law certainty when required evidence or coverage is unresolved. |

The stricter professional release standard and the v5 five-dimension blind benchmark are defined in [PROFESSIONAL-ACCURACY-STANDARD.md](PROFESSIONAL-ACCURACY-STANDARD.md). Passing a synthetic benchmark establishes the stated regression result, not universal superiority over qualified professionals; a broader comparative claim requires a controlled human study.

## Production progression

The current local baseline is intentionally simple: SQLite FTS5, an independent canonical-file scanner, deterministic metadata filters, candidate temporal links, RRF, applicability gating, official-source snapshots, clause-level source bindings, evidence packets, operational briefs and deterministic checks. It still does not prove semantic entailment. Add dense retrieval only after a fixed evaluation set demonstrates improved recall without reducing citation precision. Add a graph database only when approved relationship traversal becomes too large or slow for JSON/SQLite.
