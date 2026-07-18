# Milestone 10 - LLM Gateway and Structured Job Scoring

## Goal

Add a provider-neutral LLM gateway that returns schema-valid, explainable job scores while enforcing cost, retry, privacy, and reproducibility controls.

## Codex versus runtime

Codex builds and tests the software. The running application calls a configured runtime provider through an API or a local model. Do not automate the ChatGPT web UI. API keys and billing are separate from the ChatGPT subscription.

## Score dimensions

Each 0-10 with evidence and confidence:

- service match;
- portfolio evidence strength;
- budget/rate fit;
- scope clarity;
- timeline feasibility;
- client/risk quality;
- geography/time-zone compatibility;
- strategic value;
- effort-to-reward ratio.

Return:

- overall fit score;
- decision: `reject`, `review`, or `priority`;
- reasons;
- missing information;
- red flags;
- recommended service angle;
- suggested pricing approach, not a fabricated exact quote;
- relevant evidence queries;
- confidence;
- model/prompt/schema versions.

## Structured output

Use JSON Schema/Pydantic validation. A model response that does not validate is not a score. Retry once with repair instructions, then mark `SCORE_FAILED` and preserve diagnostics without blocking the pipeline.

## Gateway features

- `LLMProvider` interface.
- OpenAI Responses API implementation.
- deterministic fake provider for tests.
- optional local provider adapter later.
- model names in environment/config.
- timeouts and bounded retries.
- `store: false` when supported and appropriate.
- token/usage capture.
- daily and per-job budget ceilings.
- prompt and schema versioning.
- content minimization before sending.

## Prompt design

The scoring prompt must:

- include structured profile constraints, not a giant résumé;
- distinguish hard rules already evaluated from subjective dimensions;
- require quotations or field references from the job for each reason;
- prohibit assumptions about client quality, budget, or required deliverables;
- treat missing data explicitly;
- avoid gender/nationality/age or other irrelevant personal inferences.

## Threshold strategy

Initial configurable example:

- `< 5.5`: low fit;
- `5.5-7.4`: review;
- `>= 7.5`: priority.

Do not auto-discard permanently during the pilot; archive low-fit items so false negatives can be measured.

## Required deliverables

- provider interface and implementations;
- scoring schemas;
- prompt templates with versions;
- budget guard;
- fake provider and recorded non-sensitive test responses;
- score explanation UI/CLI;
- evaluation set.

## Codex execution prompt

```text
Implement Milestone 10 only. Build a provider-neutral LLM gateway with an OpenAI Responses API implementation using structured outputs, a fake provider, prompt/schema versioning, cost limits, and validated scoring. Do not hardcode a model. Add tests for malformed output, timeout, retry, budget exhaustion, missing data, and reproducibility metadata.
```

## Acceptance criteria

- [ ] All accepted scores validate against schema.
- [ ] Tests never call paid APIs by default.
- [ ] Model and prompt versions are stored with each score.
- [ ] Daily budget and per-job call limits stop further calls cleanly.
- [ ] Reasons point to actual job fields/text.
- [ ] Low scores remain inspectable during pilot.
