# Milestone 12 - Proposal Generation and Factuality Guardrails

## Goal

Generate concise, platform-appropriate proposals that sound human, answer the actual brief, use verified evidence, and never overstate experience.

## Proposal output schema

- opening line tailored to the job;
- concise understanding of the client’s need;
- 1-3 relevant capability/evidence statements;
- proposed approach or first steps;
- timing/rate framing when supported;
- one useful question when needed;
- portfolio link where allowed;
- evidence IDs supporting every factual claim;
- warnings and missing information;
- confidence and quality scores.

## Style rules

- Default 100-180 words; platform-specific limits configurable.
- Avoid generic enthusiasm and résumé dumps.
- Do not repeat the whole job description.
- Do not claim the user “has done the exact same project” without direct evidence.
- Do not promise impossible turnaround.
- Do not state a fixed price when scope is unclear; propose a range or request files.
- Mention 3D/architectural capability only where relevant.
- Include `https://www.behance.net/47pixels` unless links are disallowed.
- Preserve natural, slightly conversational English rather than over-polished AI phrasing.

## Claim ledger

Before generation, construct a ledger:

```text
claim_id -> evidence_ids -> allowed wording -> restrictions
```

After generation, extract factual claims and verify each against the ledger. Unsupported claims block review and require regeneration or manual edit.

## Quality gates

- relevance to job;
- factual support;
- no prohibited platform/contact content;
- no sensitive or discriminatory inference;
- no copied phrases longer than allowed from the posting;
- length and tone;
- actionable question;
- rate/timeline consistency;
- no hidden prompt injection from job text.

Treat job descriptions as untrusted data. Delimit them and instruct the model not to follow embedded instructions unrelated to job analysis.

## Proposal variants

Generate one default draft. Optional variants are user-triggered:

- short/direct;
- premium consultative;
- technical production-focused;
- 3D visualization-focused.

Do not generate multiple drafts automatically for every job; it increases cost and review burden.

## Required deliverables

- proposal schemas and generator;
- prompt-injection defenses;
- claim ledger and validator;
- quality checks;
- revision history;
- platform template configuration;
- golden proposal evaluation set.

## Codex execution prompt

```text
Implement Milestone 12 only. Build evidence-grounded proposal generation with one default concise draft, a claim ledger, unsupported-claim blocker, prompt-injection handling, platform-specific length/link rules, and immutable revisions. Add golden tests using design, packaging, Amazon, 3D, and architecture job fixtures.
```

## Acceptance criteria

- [ ] Every factual claim maps to verified evidence or is explicitly framed as a proposed approach.
- [ ] Unsupported claims block the draft from review.
- [ ] Proposal-only concepts cannot become completed-work claims.
- [ ] Job-text prompt injection is neutralized.
- [ ] Portfolio link is included only when policy/template allows it.
- [ ] Drafts meet human tone and length benchmarks.
