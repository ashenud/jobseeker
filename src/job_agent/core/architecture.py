"""Machine-readable modular-monolith boundaries exposed by the API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModuleBoundary:
    name: str
    responsibility: str
    forbidden_responsibility: str
    depends_on: tuple[str, ...]


MODULE_BOUNDARIES: tuple[ModuleBoundary, ...] = (
    ModuleBoundary(
        "policy",
        "Evaluate current permission for an exact action before external I/O.",
        "Implement platform transport or grant missing authority.",
        ("core",),
    ),
    ModuleBoundary(
        "sources",
        "Retrieve permitted source records and preserve raw provenance.",
        "Score jobs, draft proposals, or bypass policy.",
        ("core", "policy", "providers"),
    ),
    ModuleBoundary(
        "normalization",
        "Convert raw source records into canonical jobs and fingerprints.",
        "Perform network I/O or provider-specific submission.",
        ("core",),
    ),
    ModuleBoundary(
        "rules",
        "Apply deterministic eligibility and priority rules.",
        "Call an LLM or mutate proposal/application state.",
        ("core",),
    ),
    ModuleBoundary(
        "scoring",
        "Request and validate structured provider-neutral scoring.",
        "Select a provider/model or approve a job.",
        ("core", "providers"),
    ),
    ModuleBoundary(
        "knowledge",
        "Store eligible evidence and retrieve relevant evidence records.",
        "Invent evidence or generate unsupported claims.",
        ("core", "providers"),
    ),
    ModuleBoundary(
        "proposals",
        "Generate revisions and enforce claim-to-evidence validation.",
        "Submit, message, or edit a locked revision in place.",
        ("core", "knowledge", "providers"),
    ),
    ModuleBoundary(
        "review",
        "Own human edits, approval, rejection, and proposal locking.",
        "Treat approval as external transmission.",
        ("core", "proposals"),
    ),
    ModuleBoundary(
        "submission",
        "Prepare manual packages and gate any separately authorized connector write.",
        "Infer permission from approval or run unattended writes.",
        ("core", "policy", "providers", "review"),
    ),
    ModuleBoundary(
        "crm",
        "Own application outcomes, timeline, and follow-up drafts.",
        "Rewrite proposal history or send a follow-up without approval.",
        ("core",),
    ),
    ModuleBoundary(
        "workers",
        "Retry and schedule idempotent application-service commands.",
        "Contain domain rules or depend on SubmissionConnector.",
        ("core",),
    ),
    ModuleBoundary(
        "web",
        "Expose typed local HTTP and server-rendered review operations.",
        "Own business transactions or call providers directly.",
        ("core",),
    ),
)

DEPENDENCY_RULE = (
    "Transport and worker adapters depend inward on application and domain contracts; "
    "domain contracts never depend on FastAPI, Celery, SQLAlchemy, or a provider SDK."
)
