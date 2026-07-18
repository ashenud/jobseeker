# 94 - Test and Evaluation Dataset Guide

## Dataset folders

```text
tests/fixtures/sources/<platform>/
tests/fixtures/jobs/
tests/evals/scoring/
tests/evals/retrieval/
tests/evals/proposals/
tests/evals/adversarial/
```

## Record format

Each example includes:

- synthetic or permission-safe job text;
- expected service categories;
- hard rule outcome;
- expected score range and decision;
- required red flags/missing information;
- relevant evidence IDs;
- forbidden claims;
- expected proposal characteristics;
- human labeler and version.

## Minimum starter set

- 8 packaging/label;
- 6 Amazon/e-commerce creative;
- 5 brand identity;
- 5 3D product visualization;
- 4 architectural visualization;
- 6 general print/catalog/social;
- 10 irrelevant or outside-scope;
- 8 low-budget/risky/ambiguous;
- 8 adversarial/prompt-injection;
- 4 concept-versus-completed evidence cases.

## Data rules

- Prefer synthetic briefs modeled on real patterns.
- Remove names, contact details, and confidential files.
- Do not copy full copyrighted postings into a public repository.
- Keep private benchmark additions under ignored directories.
- Version labels and expected outputs.
