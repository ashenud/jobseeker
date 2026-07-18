# 00 - Codex Execution Pattern

## Fresh-context milestone execution

- Treat each file in `docs/prompts/` as an independent fresh-context instruction.
- Start by reading `AGENTS.md`, `IMPLEMENTATION_STATUS.md`, `docs/milestones/00-index.md`, the current milestone document, and every pattern file listed by the prompt.
- Run one milestone at a time in sequence. For prompts/milestones `00`-`22`, continue through milestones sequentially, treating each milestone as a fresh phase with its own instruction-reading, plan, implementation, checks, record updates, and commit.
- Before edits, write a concise implementation plan and list expected files to change.
- Prefer small vertical slices that satisfy the milestone acceptance criteria without speculative framework work.

## Codex features to use

- Use `AGENTS.md` for durable repository rules and nested `AGENTS.md` files only if a subtree needs stricter local rules.
- Use project configuration/hooks only for mechanical checks that can be run locally and documented in the repository.
- Dispatch sub-agents for parallel instruction reading, research, planning, review, test-analysis, record-update preparation, handoff preparation, or disjoint implementation slices for the current milestone. Assign explicit write ownership, avoid overlapping edits, and keep the coordinating agent responsible for integration, compliance decisions, final checks, commits, PR metadata, and milestone advancement. Sub-agents must not bypass policy gates or perform external submissions.
- Use MCP/tools only for live external data or repository-specific automation when explicitly available in the current session.
- If a requested Codex feature is not available in the current session, document the limitation and implement the closest repository-native control.

## Completion rules

- Run every milestone verification command plus the repository-wide fast test suite.
- Show failures honestly and leave the milestone `TODO` or blocked if checks fail.
- Update `IMPLEMENTATION_STATUS.md`, `CHANGELOG.md`, and ADRs only after acceptance criteria pass.
- Commit with `milestone-XX: <result>` for implementation milestones or `docs: <result>` for documentation-only orchestration changes. Commit each milestone before advancing to the next one.
