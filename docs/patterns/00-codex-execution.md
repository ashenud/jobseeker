# 00 - Codex Execution Pattern

## Fresh-context milestone execution

- Treat each file in `docs/prompts/` as an independent fresh-context instruction.
- Start by reading `AGENTS.md`, `IMPLEMENTATION_STATUS.md`, `docs/milestones/00-index.md`, the current milestone document, and every pattern file listed by the prompt.
- Work on one milestone only. Do not implement later milestones except for a directly required dependency fix explicitly authorized by the prompt or user.
- Before edits, write a concise implementation plan and list expected files to change.
- Prefer small vertical slices that satisfy the milestone acceptance criteria without speculative framework work.

## Codex features to use

- Use `AGENTS.md` for durable repository rules and nested `AGENTS.md` files only if a subtree needs stricter local rules.
- Use project configuration/hooks only for mechanical checks that can be run locally and documented in the repository.
- Use sub-agents only for parallel read-only review, research, or test-analysis tasks; the main agent remains responsible for reading instructions and making final edits.
- Use MCP/tools only for live external data or repository-specific automation when explicitly available in the current session.
- If a requested Codex feature is not available in the current session, document the limitation and implement the closest repository-native control.

## Completion rules

- Run every milestone verification command plus the repository-wide fast test suite.
- Show failures honestly and leave the milestone `TODO` or blocked if checks fail.
- Update `IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, and ADRs only after acceptance criteria pass.
- Commit with `milestone-XX: <result>` for implementation milestones or `docs: <result>` for documentation-only orchestration changes.
