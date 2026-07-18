# 90 - Data Contracts and JSON Schemas

This supporting document is the canonical checklist for public domain contracts. Implement exact Pydantic/JSON Schema definitions during the referenced milestones.

## ScoreResult

```json
{
  "overall_score": 8.1,
  "decision": "priority",
  "confidence": 0.84,
  "dimensions": {
    "service_match": {"score": 9, "reasons": ["Packaging and dieline work is explicitly required."]},
    "portfolio_evidence": {"score": 8, "evidence_queries": ["packaging labels print ready"]},
    "budget_fit": {"score": 7, "missing": ["final SKU count"]},
    "scope_clarity": {"score": 8},
    "timeline_feasibility": {"score": 8},
    "client_risk": {"score": 7},
    "strategic_value": {"score": 8}
  },
  "red_flags": [],
  "missing_information": ["Number of SKUs", "Dielines available?"],
  "suggested_angle": "Lead with packaging production and 3D mockup capability.",
  "pricing_approach": "Quote after confirming SKU count and dieline readiness.",
  "prompt_version": "score-v1",
  "schema_version": "1.0"
}
```

## EvidenceChunk

```json
{
  "chunk_id": "uuid",
  "document_id": "uuid",
  "title": "Verified project title",
  "text": "Evidence text",
  "services": ["packaging_label", "3d_product_visualization"],
  "verification_state": "verified_public",
  "claim_level": "completed_work",
  "public_url": "https://...",
  "restrictions": [],
  "content_hash": "sha256"
}
```

## ProposalResult

```json
{
  "body": "Proposal text",
  "opening": "Tailored first line",
  "question": "One scope question",
  "evidence_links": [
    {"claim_text": "I handle print-ready dielines...", "evidence_ids": ["uuid"]}
  ],
  "warnings": [],
  "platform_checks": {
    "length_ok": true,
    "external_link_allowed": true,
    "contact_details_allowed": false
  },
  "prompt_version": "proposal-v1",
  "schema_version": "1.0"
}
```

## PolicyDecision

```json
{
  "platform_id": "behance",
  "action": "discover",
  "mode": "manual_only",
  "allowed": false,
  "reason": "Automated retrieval not enabled; use manual capture.",
  "policy_version": "2026-07-18.1",
  "review_due_at": "2026-10-18T00:00:00Z"
}
```

## SubmissionConfirmation

Must include application, destination, locked proposal checksum, action, user, issued/expiry time, nonce, and single-use state. Store only a secure hash of the token.

## Versioning

Every persisted LLM output stores model, provider, schema, prompt, profile, and evidence-set versions. Re-running after a version change creates a new run; it never overwrites history.
