# Milestone 03 - Positioning Profile and Success Metrics

## Recovery gate

Validate the profile, scoring taxonomy, demo fixtures, and evidence references
inside the Docker tooling container. Tests must reject missing required fields,
dangling evidence IDs, unverifiable proposal claims, and contradictory rate or
budget settings. Never invent portfolio facts to satisfy this gate.

## Goal

Convert the owner’s experience, services, rates, constraints, portfolio links, preferred tone, and exclusions into structured source data. This becomes the factual base for filtering and proposal generation.

## Required deliverables

- `config/profile.yaml` created from `config/profile.example.yaml`
- `config/scoring.yaml`
- `data/private/portfolio_manifest.yaml`
- `data/private/proposal_style_anchors/README.md`
- `docs/SUCCESS_METRICS.md`
- schema validation and tests

## Positioning profile sections

### Identity

- Display name.
- Primary title: Senior Graphic Designer / 3D Visualizer.
- Portfolio URL: `https://www.behance.net/47pixels`.
- Time zone and working-hours overlap.
- Languages and communication level.

### Core services

1. Packaging and label design, dielines, print-ready production.
2. Brand identity and visual systems.
3. Amazon listing images, A+ content, and product storytelling.
4. 3D product modeling, mockups, and photoreal rendering.
5. Architectural/interior visualization.
6. Catalogs, presentations, brochures, social and advertising assets.

### Evidence-backed strengths

Record each capability as an evidence ID rather than prose alone. Example:

```yaml
- capability_id: packaging_print_production
  claim: "Experienced in packaging, dielines, labels, and print-ready files."
  evidence_ids: [portfolio_packaging_01, client_case_farla_01]
  allowed_in_proposals: true
```

### Constraints and exclusions

- Minimum acceptable project budget by service.
- Minimum hourly rate.
- Unavailable geographies or working-hour requirements.
- Industries or deliverables to avoid.
- Whether unpaid tests are rejected or conditionally accepted.
- Maximum active applications per day.
- Preferred project duration.

### Tone

- Human, concise, direct, confident but not exaggerated.
- No generic opening such as “I am thrilled to apply.”
- Mention one or two relevant capabilities, not the whole résumé.
- Ask one useful question when it improves qualification.
- Include the portfolio link in every proposal unless platform rules prohibit external links.

## Success metrics

Measure the funnel instead of “number of jobs scraped.” Suggested initial metrics:

- relevant jobs surfaced per day;
- percentage of surfaced jobs accepted for review;
- proposal draft acceptance without major rewrite;
- median time from discovery to review;
- applications submitted;
- replies, interviews, offers, wins;
- response and win rates by platform/service;
- LLM cost per reviewed job and per reply;
- false-positive rate;
- user-reported trust score for proposal factuality.

Set initial targets conservatively, then replace them with baseline data after the pilot. Example pilot targets:

- at least 80% of reviewed jobs are genuinely relevant;
- at least 60% of drafts need only light edits;
- zero invented portfolio claims;
- less than two minutes median review time;
- zero unauthorized external actions.

## Data hygiene

- Keep contact details and proposal history under `data/private/`, ignored by Git.
- Never train on or embed client-confidential documents without permission.
- Separate `verified` portfolio evidence from `draft`, `concept`, or `proposal-only` work.
- Add a field that marks HABIT[SPEC]-type concepts as proposal/concept work so the generator cannot represent them as completed client work.


## Acceptance criteria

- **M03-AC01:** The canonical profile, scoring configuration, portfolio
  manifest, and KPI definitions validate together through one documented CLI
  command with strict schemas and safe failure output.
- **M03-AC02:** Every proposal-eligible claim resolves to at least one uniquely
  identified, eligible, owner- or publicly verified evidence record.
- **M03-AC03:** Concept, speculative, proposal-only, unverified, confidential,
  or otherwise restricted evidence cannot support a completed-client-work
  claim.
- **M03-AC04:** Minimum rate, global and service budgets, geography and overlap
  rules, unpaid-test policy, workload caps, and preferred duration are explicit;
  contradictory values fail validation.
- **M03-AC05:** KPI definitions include stable identifiers, formulas,
  zero-denominator behavior, data sources, cadence, and initial targets.
- **M03-AC06:** Git tracks only scrubbed public-safe portfolio metadata and
  documentation; contact details, private records, source files, and proposal
  history remain ignored.
