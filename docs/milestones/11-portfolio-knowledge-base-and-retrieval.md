# Milestone 11 - Portfolio Knowledge Base and Retrieval

## Goal

Build a private evidence library so proposals use only relevant, verified work rather than generic claims or hallucinated experience.

## Evidence types

- portfolio project;
- completed client case study;
- testimonial or outcome;
- technical capability;
- software/tool capability;
- industry experience;
- proposal-only concept;
- rate or process policy;
- reusable answer/style anchor.

## Verification states

- `verified_public` - publicly visible and safe to mention/link.
- `verified_private` - true but not publicly linkable; use cautiously.
- `concept_only` - may be described only as a concept/personal project.
- `proposal_only` - must never be claimed as completed.
- `unverified` - excluded from generation.
- `confidential` - excluded unless a specific permission record exists.

## Ingestion process

1. User adds Markdown/YAML records and permitted portfolio exports.
2. Parser extracts title, service, industry, role, deliverables, tools, outcomes, URL, and claim restrictions.
3. Human verifies each document.
4. Text is chunked by semantic section, not arbitrary length alone.
5. Embeddings are generated for verified eligible chunks.
6. Records are versioned; deletion triggers vector cleanup.

## Retrieval strategy

Use hybrid retrieval:

- deterministic service/category filter;
- PostgreSQL full-text search;
- embedding similarity;
- rerank by verification, direct service match, recency, and public link availability.

Return a small evidence pack, normally three to five items. More context often makes proposals less specific.

## Evidence chunk schema

- document/chunk ID;
- title and source;
- text;
- service tags;
- industries;
- tools;
- deliverables;
- claim level;
- verification state/date;
- public URL;
- embedding model/version;
- content hash.

## Privacy and updates

- Store original private files outside Git.
- Embeddings are derived data and follow the original’s deletion/retention policy.
- Re-embed only changed content.
- Do not ingest entire client emails or contracts as shortcuts.
- Provide export and delete commands.

## Required deliverables

- evidence models and ingestion CLI/UI;
- chunking and embedding pipeline;
- hybrid retrieval service;
- evidence verification interface;
- seeded portfolio manifest with the owner’s approved public portfolio URL;
- tests for exclusion states and deletion.

## Codex execution prompt

```text
Implement Milestone 11 only. Build the verified evidence knowledge base, ingestion/verification flow, pgvector embeddings, and hybrid retrieval. Enforce that proposal-only, unverified, and confidential records cannot be returned for completed-work claims. Seed only safe example metadata; do not invent portfolio case studies.
```

## Acceptance criteria

- [ ] Every retrievable chunk has a verification state.
- [ ] Proposal-only work is never returned as completed evidence.
- [ ] Hybrid search returns relevant design/3D evidence for benchmark jobs.
- [ ] Changed/deleted documents update derived embeddings.
- [ ] User can inspect why each evidence item was retrieved.
- [ ] No confidential bulk data is committed to Git.
