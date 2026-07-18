# Milestone 09 - Normalization, Deduplication, and Deterministic Rules

## Goal

Turn heterogeneous postings into trustworthy canonical jobs, suppress duplicates, and reject obvious poor fits before paying for LLM inference.

## Normalization pipeline

1. Preserve raw payload.
2. Strip unsafe markup while retaining meaningful lists and line breaks.
3. Normalize Unicode, whitespace, currency symbols, and dates.
4. Parse known source fields.
5. Detect language.
6. Extract skills and service categories through deterministic dictionaries first.
7. Normalize budget without inventing values.
8. Canonicalize URLs by removing known tracking parameters.
9. Compute exact and fuzzy fingerprints.
10. Validate canonical schema and save warnings.

## Deduplication tiers

### Exact

- same platform + external ID;
- same canonical URL;
- same normalized content hash.

### Probable cross-post

Weighted comparison:

- normalized title similarity;
- client/company name;
- budget range;
- posting date proximity;
- description MinHash/similarity;
- unusual phrase overlap.

Never silently delete a probable duplicate. Link it to a canonical job with a confidence score and allow user correction.

## Deterministic rule order

1. Policy/source allowed.
2. Job not expired or too old.
3. Required location/remote eligibility compatible.
4. Banned or excluded category absent.
5. Core service relevance keywords present.
6. Budget/rate rule.
7. Workload or timing rule.
8. Client/job red flags.
9. Daily volume cap.
10. Route survivors to LLM scoring.

## User-specific service taxonomy

Include categories such as:

- packaging_label;
- brand_identity;
- amazon_ecommerce_creative;
- 3d_product_visualization;
- architectural_visualization;
- catalog_presentation_print;
- social_ad_creative;
- technical_dieline_prepress.

Keywords are weighted, and negative keywords are supported. Do not reject solely because a job uses unfamiliar wording if semantic scoring may help; use `needs_score` rather than false certainty.

## Red flags

Examples to detect and explain:

- unrealistic deliverables for budget;
- unpaid large test request;
- request to communicate or pay off-platform where prohibited;
- vague scope plus urgent deadline;
- rights transfer before payment;
- suspicious links or attachments;
- request for copied portfolio work;
- job asking for skills far outside the profile.

Red flags are advisory unless explicitly configured as hard rejects.

## Required deliverables

- normalization service and parsers;
- fingerprint and dedup service;
- rules engine with explainable results;
- taxonomy configuration;
- duplicate review UI or CLI;
- benchmark fixtures.

## Codex execution prompt

```text
Implement Milestone 09 only. Build canonical normalization, exact/probable deduplication, and an ordered deterministic rules engine based on the owner’s design/3D service taxonomy. Every decision must record rule IDs and reasons. Add tests for currencies, unknown budgets, dates, duplicate cross-posts, and red flags.
```

## Acceptance criteria

- [ ] Unknown data remains unknown rather than fabricated.
- [ ] Exact duplicate ingestion is idempotent.
- [ ] Probable duplicates are linked with confidence and can be corrected.
- [ ] Rules are configuration-driven and explainable.
- [ ] LLM calls occur only after deterministic rules.
- [ ] Test fixtures cover at least 30 varied job posts.
