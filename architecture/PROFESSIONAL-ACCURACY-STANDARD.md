# Professional-Accuracy Standard

**Baseline:** 29 August 2026  
**Priority:** accuracy, authority and reproducibility before latency or token cost

## 8 September 2026 Evaluation Clarification

The [Answer Quality Rubric](ANSWER-QUALITY-RUBRIC.md) governs subsequent interpretation of evaluation scores. Content correctness, completeness and relevant-case citation are separate dimensions. Missing answer citations or unavailable packet evidence alone cannot establish incorrectness. An evaluator may verify an uncited conclusion against applicable official sources in a separately recorded review. Where a materially relevant real case is known, its omission is a case-citation deficiency even if the conclusion is correct. Unverified and unanswered are not synonyms for incorrect, or for correct.

The workflow and v5 gates below remain provenance and release controls, and the recorded v5 result remains historical evidence. A gate failure is not automatically a semantic error. The historical sentence about fail-closed outcomes applies to justified uncertainty or a correct decision to withhold action, not automatic full credit for retrieval failure or an omitted answer. No scoring change grants operational permission or bypasses current-law release checks.

## Objective

The system is intended to perform professional-grade Australian electricity compliance research and first-pass operational analysis with greater consistency, recall and auditability than an unaided individual. It is not permitted to claim that it outperforms every qualified professional merely because it passes a synthetic benchmark. A comparative superiority claim requires a controlled, blinded human benchmark using the same questions, source cutoff and scoring rubric.

The current acceptance claim is narrower and testable: the KB must pass the independent v5 professional scenario benchmark without a critical legal-status, temporal, jurisdiction, evidence or operational-control error.

## Mandatory answer workflow

1. Identify actor, jurisdiction, conduct date, answer date, issue family and requested legal effect.
2. Run two independently formulated searches and merge them with reciprocal rank fusion.
3. Traverse reviewed event-to-provision and appellate or supersession links.
4. Freeze the evidence packet before drafting.
5. Draft material claims only from packet evidence and cite evidence IDs.
6. Reject current-law certainty unless an approved current provision version is present.
7. Run deterministic claim checks and a second independent search.
8. Require an independent reviewer to score jurisdiction, time, status, controls, and evidence or uncertainty.
9. Release only after all five dimensions pass and no critical trap is triggered.

## V5 benchmark gates

| Gate | Required result |
|---|---:|
| New professional scenarios | 100 |
| Exact or near-semantic overlap with v3/v4 | 0 |
| Named gold event recall in Top 18 | 100% |
| Material claims citing frozen-packet evidence | 100% |
| Current-law claims citing an approved current provision | 100% |
| Jurisdiction and scope score | 100 / 100 |
| Temporal applicability score | 100 / 100 |
| Legal and procedural status score | 100 / 100 |
| Operational control score | 100 / 100 |
| Evidence and uncertainty score | 100 / 100 |
| Critical errors | 0 |
| Final total | 500 / 500 |

Fail-closed outcomes are correct answers when the source, current version, jurisdiction, status or public-archive coverage is insufficient. A high answer rate is not an accuracy metric.

## Critical errors

Any one of the following blocks release regardless of aggregate score:

- applying a rule outside its jurisdiction or operative period;
- treating a future, repealed or superseded provision as current;
- treating allegations, notices without admissions, undertakings, administrative outcomes or technical reports as final court findings;
- relying on a quashed or displaced proposition;
- claiming public-corpus exhaustiveness while a relevant source family has an archive gap;
- inventing a clause, amount, date, entity or legal outcome;
- citing evidence that was not in the frozen packet;
- giving operational clearance where live verification or accountable escalation is required.

## Human accountability

The KB can exceed unaided human consistency in retrieval, chronology, status labelling and evidence preservation. It does not replace the accountable legal, regulatory, engineering or safety officer who has access to privileged facts, current licences, plant-specific standards, contracts and regulator communications. Binding advice and high-impact operational release remain subject to the organisation's approval matrix.

## Continuous regression

Every material corpus, provision, appeal-status, retrieval or checker change must rerun:

- repository validation;
- v3 and v4 regression banks;
- v5 novelty and retrieval tests;
- v5 blind answering and independent five-dimension audit;
- known fail-closed architecture regressions.

The benchmark remains frozen for regression. New questions are added as a later version rather than silently rewriting failed questions, except where the gold key itself is proven wrong and the correction is documented.

## Current verified result

The final v5 release audit passed 100/100 questions and 500/500 dimensions with zero critical errors. The first blind audit was 55 pass, 43 partial and 2 fail at 440/500; remediation therefore remains visible rather than being replaced by the final aggregate. Retrieval recovered all named gold events for 94/94 applicable questions, the final 309 material claims are frozen-packet bound, and the deterministic checker reports zero blocking errors and zero retrieval warnings. This benchmark does not replace the stricter runtime clause-binding and accountable-approval gates.

This result satisfies the repository acceptance claim only. It does not establish universal superiority over qualified professionals or public-corpus exhaustiveness.
