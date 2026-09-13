# Risk-Tiered Answers and Approval Examples

**Status:** proposed interaction and policy design, not implemented workflow or legal clearance  
**Date:** 5 September 2026

## Point 5 in practice

Use a concise answer first, an expandable evidence/case dossier, and a persistent decision record only when needed. Do not impose professional approval on every information request. The named accountable person approves material action or an exception within lawful discretion, not the act of reading a legal explanation. Their approval cannot override an unresolved source gap, missing material facts or a legal prohibition.

| Request | User receives | Individual approval |
|---|---|---|
| Explain a term or compare procedural case statuses | Direct domain explanation, sources, date and relevant limits | No, unless the query becomes a material operational decision |
| Validated routine scenario with complete facts and current authority | Direct conditional answer, checklist and references under a versioned reviewed policy | No additional professional sign-off solely for the answer; ordinary business authorisation remains applicable |
| Material action such as a customer-harm risk, market submission exception or reportable incident decision | Recommendation, exact obligations, fact/evidence gaps, similar cases and an approval brief | Named authorised person before material execution; unresolved legal interpretation goes to a qualified specialist |
| Missing controlling text, contradictory authority or unresolved material facts | Supported partial answer, precise blocker and the next question or evidence request | Approval cannot turn missing evidence into a legal clearance |

Do not use model confidence or money value alone to select the tier. Consider customer vulnerability, reversibility, aggregate scale, notification deadlines, licence exposure, source certainty and whether the organisation already approved the precise workflow and conditions. Thresholds and delegations are enterprise policies to be confirmed, not universal legal rules.

## Example A: a routine query

**Question:** "What is the difference between a paid infringement notice and a court judgment, and how should we describe historical cases in an internal briefing?"

**Proposed answer form:** give the distinction, qualify the particular notice under its governing scheme, cite the actual notice or judgment, and preserve the case's status and date. Avoid treating payment or an allegation as a judicial finding. Show a reusable wording example tied to the verified record. This is a research answer: no approval task and no execution permission are created.

The point is self-service resolution of a repeatable research question. A one-line disclaimer followed by "ask a lawyer" would not meet the business objective.

## Example B: a material enterprise scenario

**Hypothetical question:** "Our Victorian electricity retailer has a residential customer with arrears, a disputed bill and a possible life-support flag. A debt-collection referral is queued for tomorrow. Can we send it?"

This example is an internal precautionary-control design. It is not a conclusion about the legality of that customer's referral, and it does not assert a blanket prohibition or a statutory deadline.

**Decision panel, proposed output:**

- **Answer:** do not release the queued referral on the evidence currently supplied. Hold this proposed action for targeted checks; this is an internal precaution, not a completed legal determination.
- **What is known:** jurisdiction and retailer role were supplied. Arrears, a dispute and a possible medical-equipment flag are reported, not independently verified.
- **What changes the answer:** correct legal entity and licence, customer class, bill accuracy, complaint stage, assistance arrangements, flag status, intended referral activity, any other applicable customer protections and the proposed action date.
- **Legal basis panel:** populate exact operative clauses, definitions, exceptions, commencement dates and source spans after verification. A PDF page range or an old case cannot substitute. In this demonstration, current-law verification is pending.
- **Immediate work:** assign a billing/complaint owner; obtain authorised access to relevant records; confirm the intended action and safeguard status; preserve the review record. Assess any urgent safety or notification duties separately so a referral hold does not delay them.
- **Historical analogy:** EWOV reported systemic ENGIE billing-complaint handling issues and a referral to the ESC in its [28 November 2025 account](https://www.ewov.com.au/news/esc-fines-engie-after-ewov-investigation). This illustrates the importance of addressing complaints and root causes. It does not establish that the present referral is unlawful, and it is not a life-support disconnection precedent or a court judgment.
- **Approval:** when the exact rules and material facts are resolved, a named delegate reviews the remaining recommendation. Only residual disputed legal interpretation goes to the specialist; the specialist should not have to recreate the research.
- **Reuse limit:** the approval applies only to the identified facts, action, evidence and policy version. Changed facts, authority or expiry invalidate reuse.

**Illustrative record, not generated production capability:**

```json
{
  "record_id": "SYNTHETIC-EXAMPLE-NOT-A-REAL-CUSTOMER",
  "risk_tier": "material-action-review",
  "answer_state": "supported-partial-answer",
  "recommendation": "hold-proposed-referral-pending-material-checks",
  "legal_clearance": "not-established",
  "action_release_state": "blocked",
  "may_execute": false,
  "current_authority_verified": false,
  "missing_evidence": ["operative-clause-review", "bill-and-dispute-records", "safeguard-status"],
  "accountable_owner": null,
  "approver_identity": null,
  "approval_scope": null,
  "approval_time": null,
  "policy_version": null,
  "evidence_packet_hash": null,
  "expires_at": null
}
```

An implemented version must authenticate the approver, check delegated authority, verify non-overridable blockers, bind the full facts and evidence to the record, persist audit events and invalidate stale decisions. A JSON value changed to `approved` must have no authority by itself. The current generator implements none of these transitions and always emits `may_execute: false`.

## Cost-saving mechanism

The system removes repeated searching, citation assembly, routine issue classification, case comparison and checklist preparation. Reviewed policies can be reused on genuinely equivalent low-risk matters only while facts and authority remain valid. Reviewers concentrate on unresolved material judgment and approval. Measure the remaining review minutes and unnecessary escalation; do not assume the presence of an approval brief itself creates a saving.
