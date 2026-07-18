# Documentation map

This directory has one authoritative copy of each document type.

| Location | Purpose |
|---|---|
| `milestones/` | Product and engineering acceptance specifications, in dependency order |
| `prompts/` | Thin Codex entry prompts that invoke the repository milestone skill |
| `patterns/` | Technical implementation patterns shared by milestones |
| `adr/` | Accepted architectural decisions |
| `00`-`99` root documents | Cross-milestone contracts, schemas, research, and operational references |
| Named root documents | Living product, architecture, security, pilot, and operations records |

## Sources of truth

- Progress: `IMPLEMENTATION_STATUS.md`
- Execution order and dependency gates: `milestones/00-index.md`
- Working-demo contract: `DEMO_ACCEPTANCE.md`
- Prompt ledger: `prompts/README.md`
- Durable Codex rules: `../AGENTS.md`
- Repeatable Codex workflow: `../.agents/skills/jobseeker-milestone/SKILL.md`

Numbered milestone documents must exist only in `milestones/`. Do not recreate
`docs/01-...md` through `docs/22-...md` at the documentation root.
