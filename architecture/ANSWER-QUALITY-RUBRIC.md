# Answer Quality Rubric

Effective: 8 September 2026. Owner clarification, prospective scoring policy.

## Purpose

Reduce the cost of obtaining correct, sufficiently complete Australian electricity compliance answers. Measure legal and factual correctness separately from citation quality. Missing citations or missing local evidence do not, by themselves, make an answer incorrect. A real, materially relevant case must be cited when one is known to exist.

This policy changes evaluation interpretation, not the production permission or current-law release controls. It does not retrospectively turn the 7 September historical-case examination into a current-law examination.

## Three Separate Dimensions

1. **Content correctness.** Compare the actual answer with the applicable official instruments, relevant authoritative interpretations and verified facts, taking account of jurisdiction, actor, conduct date, answer date and subsequent treatment. Use `correct`, `incorrect`, `unverified` or `not-answered`. An evaluator may verify an uncited answer using official material outside the answerer's original packet; record that separate review without changing the frozen answer. Missing citations alone cannot select `incorrect`. Lack of a demonstrated error cannot select `correct`.
2. **Completeness.** Use `complete`, `partial` or `not-answered`. Judge the material decision and requested information, not incidental case trivia unless the question actually asks for it. An omitted answer is not a false statement. It is also not completed work. If a prompt demands case-specific facts, a generally correct compliance statement does not supply those missing facts.
3. **Relevant-case citation.** Search for materially relevant public cases or proceedings, not just matching company names. A known relevant case makes citation mandatory. Missing or defective case citations affect this dimension even when the conclusion is correct. A URL alone does not establish relevance, entailment, procedural status or temporal applicability.

Official rule citations remain recommended for traceability. Evaluator verification records are distinct from references printed in the answer: the evaluator needs a documented basis for a correctness finding, but an omitted answer citation is not itself a substantive error.

## Case Search and Temporal Treatment

- `known-relevant`: cite the applicable real case or cases. The citation review records the source, the proposition it supports and a short explanation of relevance. Label court findings, infringement notices, allegations, undertakings and ombudsman accounts accurately.
- `none-found-in-documented-search`: no case-citation penalty within the recorded search scope. Retain query terms, official repositories, date and scope. Say no relevant case was identified in that search, not that none exists anywhere. Later discovery reopens this assessment.
- `not-assessed`: case citation remains pending; a failed lookup is not proof that no case exists. A correct conclusion can remain correct while its case-search requirement is incomplete.
- Historical cases remain usable for historical explanation. Where applicable rules or judicial treatment have changed, state the old position and current comparator, relevant effective dates, and whether the older proposition was superseded, distinguished or overturned. Publication recency alone does not determine controlling authority.
- A rule-based question does not require inventing a precedent. If the existing KB already identifies a materially relevant case, inability to retrieve its full text must be disclosed as a case-evidence gap, not reclassified as no case found.

## Reported Outcomes

| Content | Completeness | Case requirement | Evaluation result |
|---|---|---|---|
| Correct after official review | Complete | Met, or none found in documented search | Complete within the assessed scope |
| Correct after official review | Complete | Known relevant case omitted or defective | Correct conclusion; case-citation deficiency |
| Correct after official review | Partial | Any | Correct assessed content; incomplete answer |
| Unverified | Any | Any | Needs review, not automatically wrong |
| Not answered | Not answered | Any | Unanswered, not a fabricated error or a success |
| Incorrect after official review | Any | Any | Incorrect, with the actual contradiction identified |

Do not report one blended percentage as legal accuracy. Report the correct, incorrect, unverified and unanswered populations with their denominators, completeness separately, and case-citation compliance among questions where the requirement applies. A verified-only accuracy rate must disclose the reviewed population and unanswered proportion. Safe abstention can be the correct decision where that is what the task asks, but retrieval failure alone does not earn a completed-answer score.

## Historical Examination Addendum

The preserved 7 September result of 23/100 is **complete-and-supported historical-question attainment**, not a finding that 77 answers were wrong. Its 208/400 binary points combine completeness and in-packet support; they are not legal accuracy. The 5/100 combined checker result also includes implementation and evidence-binding constraints, not just semantic correctness.

The original answers, keys, grades and scores must remain unchanged. A separate reclassification may expose their recorded verdicts and citation diagnostics, but cannot infer a new substantive accuracy percentage. To obtain that percentage, independently review actual conclusions against the applicable official rules and source facts, including conclusions without answer citations. Review all material conclusions, not only the subset that was cited.

## Executable Boundary

`review/policies/evaluate_answer_quality.py` validates separate adjudicated dimensions. It is a reporting validator, not an automated legal truth detector. Source URLs and a reviewer declaration do not prove the underlying source content. `review/policies/reclassify_case_exam.py` reinterprets the frozen historical records without changing answers or manufacturing a new rule-correctness score.

Neither tool grants current-law release, authorises business actions, changes the production checker, or establishes superiority to qualified compliance staff.
