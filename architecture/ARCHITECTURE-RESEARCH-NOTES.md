# Architecture Research Notes

## Status and research boundary

- Research date: 2026-08-29.
- Scope: architecture research for an accuracy-first Australian electricity legal and compliance knowledge base.
- Source policy: only official project repositories, official product documentation, and original research publications were considered. Every external page was treated as untrusted input. Feature and performance statements remain claims by their respective authors or vendors unless independently validated in this repository.
- This note is an architecture sidecar, not a legal opinion, a product selection, or evidence that any candidate system meets the knowledge base's legal-accuracy requirements.

## Executive conclusion

The recommended design is not plain vector RAG, Microsoft GraphRAG, OpenSPG KAG, or LightRAG as a complete system of record. It is a **temporal, provenance-gated evidence system with hybrid retrieval and a derived knowledge graph**.

The authoritative layer should be a deterministic evidence ledger containing official source snapshots, cryptographic hashes, document and paragraph identifiers, jurisdiction, instrument version, commencement and cessation dates, event date, decision date, procedural status, appeal history, and source authority. Search indexes, embeddings, graph edges, summaries, and model-generated labels should be disposable derivatives that can be rebuilt from that ledger. They must never overwrite or silently amend canonical legal facts.

For retrieval, exact lexical search and structured legal filters should be combined with semantic retrieval. Reciprocal rank fusion can merge independently ranked candidate lists, but rank is only a recall mechanism. It does not establish legal authority, temporal applicability, or factual correctness. A deterministic provenance and temporal gate must run after retrieval and before any answer is released.

For answering, use two independent searches and two independent checks:

1. Search A targets exact entities, clauses, instruments, dates, jurisdictions, case names, and identifiers.
2. Search B independently looks for current-law versions, amendments, repeals, appeals, later decisions, contrary authority, and regulator corrections.
3. Check A verifies every material claim against an exact source span and validates source authority, date, jurisdiction, and procedural status.
4. Check B independently re-searches the strongest conclusion and tests for temporal conflict, supersession, appeal, reversal, and omission.
5. The system fails closed when a material claim lacks authoritative support, a current-law version cannot be established, sources conflict, or a proceeding is not final.

This design can use selected components from the reviewed projects, but legal truth should remain outside all model-generated graph and answer layers.

## Non-negotiable legal data model

### Canonical evidence records

Each evidence record should carry, at minimum:

- `source_id`, canonical URL, publisher, retrieval timestamp, content hash, and snapshot location;
- source class, such as legislation register, court or tribunal, regulator decision, enforceable undertaking, infringement notice, regulator media release, technical investigation, ombudsman report, or secondary report;
- jurisdiction and market scope, including NEM, WEM, Northern Territory, or retail-only scope;
- document title, stable document identifier, pinpoint paragraph, page, section, clause, schedule, or table reference;
- publication date, conduct period, event date, decision date, effective-from date, effective-to date, and knowledge-base ingestion date;
- instrument name, version, amendment history, commencement status, repeal status, and successor instrument;
- party identity and role at the relevant date;
- procedural status, including allegation, investigation, infringement notice, undertaking, commencement of proceedings, first-instance decision, appeal pending, appeal allowed or dismissed, final orders, and no-admission outcome;
- proposition supported by the exact source span and a human-review status;
- explicit links for `amends`, `repeals`, `supersedes`, `appeals`, `affirms`, `reverses`, `distinguishes`, `same_conduct_as`, and `current_equivalent_of`.

The system should use bitemporal fields: **legal validity time** records when a rule or decision applied, while **system knowledge time** records when the knowledge base learned, corrected, or superseded the record. This prevents a later update from erasing what the applicable rule was at the time of historical conduct.

### Authority and status gates

An answer should distinguish at least these states rather than calling every indexed event a proven violation:

- alleged conduct with no final determination;
- infringement or administrative penalty, including whether liability was admitted;
- enforceable undertaking or negotiated resolution;
- regulator or market-operator determination;
- first-instance judgment;
- judgment under appeal;
- final appellate position;
- technical incident with no enforcement finding;
- historical rule mapping that does not state the current obligation.

For every historical case, the answer packet should contain two separate fields: `law_applied_at_event_time` and `current_law_as_at_answer_date`. A historical decision may explain the origin of a control, but it should not be presented as the current clause unless the current instrument and later authority have been independently verified.

## Technology comparison

| Candidate | What the primary source describes | Useful role in this KB | Accuracy limitations for legal compliance | Recommendation |
| --- | --- | --- | --- | --- |
| Microsoft GraphRAG | An LLM-based indexing pipeline that extracts entities, relationships, and claims, performs community detection, generates community reports, and embeds text. Its query methods include local, global, and DRIFT search. | Corpus-level exploration, theme discovery, cross-document relationship hypotheses, and broad questions over large investigation sets. | The graph, claims, and community summaries are model-derived. A plausible relationship can therefore be an extraction or summarisation error. The official repository says the project is largely in maintenance mode, is a research project rather than an officially supported Microsoft offering, can be expensive to index, and normally requires prompt tuning. It does not provide legal temporal validity, authority ranking, appellate status, or fail-closed proof by itself. | Do not use as the canonical legal layer or default answer engine. Optionally use a pinned version as a read-only discovery index whose results must resolve to canonical evidence spans. |
| OpenSPG KAG | A framework built on OpenSPG and LLMs for professional-domain question answering. It combines knowledge and chunk mutual indexing, schema-constrained knowledge construction, semantic alignment, and logical-form-guided hybrid reasoning and retrieval. | Strongest candidate of the three graph systems for explicit domain schema, multi-hop reasoning, and tracing an issue through entities, obligations, events, and instruments. | Schema constraints reduce some ambiguity but do not make extracted facts legally true. Knowledge extraction, normalisation, semantic alignment, query decomposition, and reasoning can all introduce or propagate errors. The project's comparative performance claims are author claims, not validation on Australian electricity law. Operational complexity and schema governance are substantial. | Consider only after a reviewed temporal legal schema exists. Populate authoritative nodes and edges deterministically or through human approval. Keep model-extracted edges quarantined as hypotheses. |
| LightRAG | A lightweight graph-based RAG framework using knowledge-graph and vector layers. The repository describes dual-level retrieval, incremental updates, selective deletion, multiple chunking strategies, and multiple storage backends. | Rapid exploratory retrieval, incremental ingestion, and lower-overhead graph-plus-vector experiments. | Lightweight graph maintenance does not supply legal authority rules. Model extraction can merge similarly named entities, lose qualifiers, or connect provisions across incompatible dates or jurisdictions. Incremental deletion or rebuilding can also change derived relationships, so answers are not reproducible unless versions and snapshots are pinned. Repository claims about legal-domain quality are not a substitute for a domain benchmark. | Suitable only as an optional, derived discovery service. Do not let its graph or cached answer become evidence or current-law truth. |
| Elasticsearch hybrid search and RRF | Official documentation combines full-text and vector search and recommends reciprocal rank fusion to merge ranked lists. RRF combines ranks without requiring comparable raw scores. | Recommended retrieval backbone when operational scale warrants it: BM25 for exact legal language and identifiers, vector retrieval for paraphrases, structured filters for jurisdiction/date/status/source class, and RRF for candidate fusion. | RRF optimises rank fusion, not truth. Equal treatment of child rankings can elevate semantically similar but legally inapplicable material. Approximate vector search can omit the controlling document. Neither BM25 nor vector similarity understands repeal, commencement, appeal, or authority unless those are explicitly modelled and filtered. Product version and licensing details must be checked before procurement. | Best fit among the reviewed technologies for the retrieval layer, provided deterministic filters and post-retrieval legal gates control the answer. A smaller corpus may begin with SQLite FTS plus a separate vector index while preserving the same interfaces. |
| RAGChecker | A fine-grained RAG evaluation framework using claim-level entailment, with diagnostic retriever and generator metrics. | Useful for diagnosing retrieval recall, context precision, context utilisation, hallucination, and claim-level faithfulness on a curated benchmark. | Automated entailment is not a legal validation. A claim can be faithful to an outdated, non-authoritative, or procedurally incomplete context. Evaluation quality depends on benchmark answers and evaluator behaviour. | Use as one evaluation layer, never as the release gate by itself. Add deterministic temporal and citation checks plus expert-reviewed test cases. |
| Ragas | An evaluation toolkit with context precision, context recall, noise sensitivity, response relevancy, faithfulness, factual correctness, and related metrics; its documentation notes that LLM-based metrics can make one or more model calls. | Convenient experiment harness for comparing retrievers, prompts, rerankers, and answer policies. | LLM-judge scores can be unstable and can reward support from the wrong source version. Generic faithfulness and relevance metrics do not test authority, commencement, appeal, jurisdiction, or whether a penalty involved an admission. | Use for trend analysis and regression testing, with pinned evaluators and samples. Do not convert a high aggregate score into permission to answer. |

## Recommended architecture

### 1. Authoritative source and snapshot layer

Fetch only from an allowlisted source register. Preserve the fetched artefact, final resolved URL, retrieval time, MIME type, HTTP metadata where available, and SHA-256 hash. Keep the original artefact immutable. A changed upstream document creates a new version; it does not mutate the prior snapshot.

Authoritative-source preference should be explicit and query-dependent. A practical default is:

1. official legislation and rules registers, gazetted instruments, and official compiled versions;
2. official court or tribunal judgments and orders;
3. formal regulator determinations, infringement notices, enforceable undertakings, licence decisions, and market-operator decisions;
4. regulator technical investigations and official compliance publications;
5. regulator media releases that point to the formal record;
6. ombudsman publications and official aggregate reports;
7. reputable secondary reporting for discovery only.

A lower-ranked source can describe an event, but it cannot silently replace a higher-ranked source on the legal proposition the higher-ranked source decides.

### 2. Temporal evidence ledger

Store documents, source spans, instruments, instrument versions, provisions, events, parties, decisions, appeals, and propositions as separately addressable records. Version them append-only. Require reviewed edges for temporal and precedential relationships.

Model outputs may propose entities, tags, and edges, but each proposal remains `unverified_derived` until a deterministic parser or human reviewer binds it to an exact official span. Derived records should include the model, prompt, configuration, input hashes, and generation time so they can be reproduced or discarded.

### 3. Multiple retrieval channels

Run retrieval channels independently before fusion:

- exact identifier lookup for case numbers, instrument versions, clause numbers, ABNs, licence numbers, NMIs where lawfully stored, and canonical event IDs;
- BM25 or equivalent lexical search for exact legal phrases, party names, and uncommon terminology;
- dense or sparse semantic retrieval for paraphrases and issue descriptions;
- temporal graph traversal for amendments, repeals, successor clauses, appeals, reversals, and related conduct;
- metadata filtering for jurisdiction, sector, date interval, procedural status, source class, and authority;
- source-family completeness lookup to determine whether the corpus can support an exhaustive answer.

Use RRF only to form a candidate pool. Apply hard legal filters before and after fusion. Preserve each channel's rank and reason so retrieval is auditable.

### 4. Double search

The second search must be genuinely independent, not merely a larger `top_k`:

- Search A asks what evidence directly answers the user's facts and date.
- Search B asks what could make Search A wrong: later amendments, transitional provisions, repeals, savings clauses, appeals, later judgments, corrected regulator publications, jurisdiction mismatch, and unresolved source-family gaps.

The two searches should use separately generated query plans and should report disagreement. If the controlling current instrument is found only by Search B, the first answer draft must be discarded and regenerated.

### 5. Evidence-packet answer generation

The answer model receives a bounded evidence packet, not unrestricted corpus access. Every supplied item should include:

- exact source span and stable evidence ID;
- source URL and snapshot hash;
- source authority class;
- jurisdiction and sector;
- applicable date interval;
- procedural and appellate status;
- whether the text supports historical law, current law, or both;
- any conflict or completeness warning.

The answer schema should separate `confirmed`, `qualified`, `historical_only`, `alleged`, and `unknown`. Each material sentence should cite at least one evidence ID. The model must not fill a missing clause number, commencement date, outcome, or current-law mapping from parametric memory.

### 6. Double check and fail-closed release

Checker A should decompose the draft into atomic claims and verify that each cited span entails the claim without omitting material qualifiers. Deterministic checks should confirm that cited records exist, URLs and hashes match, date intervals overlap the question, jurisdictions match, and procedural labels are not overstated.

Checker B should receive the question and proposed conclusion, but not Checker A's reasoning. It should conduct the contradiction-oriented second search and independently identify the controlling current version and later authority.

Release is blocked when any of the following applies:

- a material claim has no exact authoritative citation;
- current-law status or the relevant date cannot be established;
- a historical provision is presented as current without a reviewed version link;
- a lower-court result is under appeal or has been reversed and the answer omits that fact;
- an allegation, infringement notice, undertaking, settlement, or technical incident is described as a final judicial finding when it is not;
- sources conflict and the conflict is unresolved;
- a requested exhaustive answer crosses a source family marked incomplete or archive-gap;
- both searches do not recover the expected controlling authority for a benchmark question.

The safe output is an explicit limitation or abstention that states what evidence is missing and which source family or temporal link requires review.

## Evaluation design

RAGChecker and Ragas can provide useful diagnostic signals, but the release suite must add domain-specific deterministic metrics:

- authoritative citation precision and recall;
- pinpoint-span correctness;
- instrument-version and provision-version accuracy;
- effective-date and transitional-provision accuracy;
- jurisdiction and market-scope routing accuracy;
- entity identity and corporate-successor accuracy;
- procedural-status accuracy;
- appeal, reversal, and supersession detection recall;
- historical-law versus current-law separation accuracy;
- source-family completeness warning recall;
- contradiction detection recall;
- correct abstention rate and unsafe-answer rate;
- reproducibility from pinned source snapshots and derived-index versions.

The benchmark should contain ordinary questions, adversarial near-duplicates, changed-law cases, cross-jurisdiction traps, same-name entities, regulator releases superseded by formal orders, proceedings later resolved on appeal, and questions whose only correct response is to abstain. Gold answers should be authored or approved by qualified reviewers and include exact evidence spans, not only prose answers.

LLM judges may score claim entailment and answer quality, but deterministic checks and reviewed gold evidence must control deployment. Track metrics per jurisdiction, issue family, time period, source class, and procedural status; a single average score can hide a dangerous failure mode.

## Adoption decision

### Recommended now

- Build the temporal evidence ledger and source snapshot discipline first.
- Implement exact and lexical retrieval with strict metadata filters.
- Add semantic retrieval as an independent recall channel and fuse candidates with RRF.
- Build the contradiction-oriented double search and independent double check before adding graph-generated summaries.
- Add a small, reviewed temporal graph for instrument succession and case appellate history.
- Use RAGChecker and Ragas only as supplemental evaluation tools alongside deterministic legal tests.

### Evaluate later

- Evaluate OpenSPG KAG if the reviewed legal schema becomes large enough that explicit multi-hop reasoning materially improves benchmark performance.
- Evaluate LightRAG for a read-only exploratory index when frequent incremental ingestion becomes an operational bottleneck.
- Evaluate Microsoft GraphRAG only for broad corpus synthesis or thematic investigation, with a pinned version and no authority to publish legal conclusions.

### Do not adopt

- Do not use vector similarity alone.
- Do not treat a generated knowledge graph as the system of record.
- Do not permit an answer model to choose the current law solely from retrieved text similarity.
- Do not let RAG evaluation scores replace temporal, authority, citation, and procedural-state validation.
- Do not claim exhaustive coverage when any relevant official source family remains unharvested, aggregate-only, blocked, or archive-gap.

## Primary sources consulted

All sources below were retrieved on **2026-08-29**.

1. Microsoft GraphRAG official repository: https://github.com/microsoft/graphrag
2. Microsoft GraphRAG official indexing overview: https://microsoft.github.io/graphrag/index/overview/
3. Microsoft GraphRAG original paper, "From Local to Global: A Graph RAG Approach to Query-Focused Summarization": https://arxiv.org/abs/2404.16130
4. OpenSPG KAG official repository: https://github.com/OpenSPG/KAG
5. KAG original paper, "KAG: Boosting LLMs in Professional Domains via Knowledge Augmented Generation": https://arxiv.org/abs/2409.13731
6. LightRAG official repository: https://github.com/HKUDS/LightRAG
7. LightRAG original paper, "LightRAG: Simple and Fast Retrieval-Augmented Generation": https://arxiv.org/abs/2410.05779
8. Elastic official hybrid-search documentation: https://www.elastic.co/docs/solutions/search/hybrid-search
9. Elasticsearch official reciprocal-rank-fusion reference: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/reciprocal-rank-fusion
10. Amazon Science RAGChecker official repository: https://github.com/amazon-science/RAGChecker
11. RAGChecker original paper: https://arxiv.org/abs/2408.08067
12. Ragas official metrics documentation: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

## Research limitations

- This was a source review, not a deployed benchmark against the repository's Australian electricity corpus.
- Repository documentation and papers describe intended behaviour and reported results; they do not prove legal accuracy for this use case.
- Product APIs, licences, dependencies, maintenance status, and performance can change after the retrieval date.
- No reviewed technology natively supplies the complete combination of Australian legal source authority, bitemporal instrument versioning, appellate status, corpus completeness accounting, and fail-closed answering required here.
