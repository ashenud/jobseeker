# Milestone 10 - LLM Gateway and Structured Job Scoring

## Recovery gate

Implement a provider-neutral gateway with a deterministic fake for tests and a
real OpenAI Responses API provider using strict structured output parsed into
Pydantic models. Provider and model come from validated configuration; secrets,
URLs, and model names are not hardcoded in domain code. Persist prompt/schema/
provider/model versions, usage, cost, latency, refusal, and retry outcomes.

Offline malformed-output, refusal, timeout, retry, budget, and idempotency tests
must pass. A bounded opt-in real-AI smoke must persist a schema-valid score. If
the required credential is unavailable, this milestone is `BLOCKED`, not `DONE`.
Use the current official Structured Outputs guidance:
`https://developers.openai.com/api/docs/guides/structured-outputs`.

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


## Acceptance criteria

- [ ] All accepted scores validate against schema.
- [ ] Tests never call paid APIs by default.
- [ ] Model and prompt versions are stored with each score.
- [ ] Daily budget and per-job call limits stop further calls cleanly.
- [ ] Reasons point to actual job fields/text.
- [ ] Low scores remain inspectable during pilot.
