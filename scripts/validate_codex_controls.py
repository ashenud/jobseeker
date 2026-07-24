#!/usr/bin/env python3
"""Structurally validate repository Codex controls and Docker-only wrappers."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import tomllib
from types import ModuleType
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".codex" / "hooks" / "enforce_docker_boundary.py"
AGENT_SPECS = {
    "milestone-planner": "read-only",
    "repository-explorer": "read-only",
    "milestone-worker": "workspace-write",
    "test-evidence-analyst": "read-only",
    "policy-release-reviewer": "read-only",
}
WRAPPERS = ("scripts/bootstrap.sh", "scripts/check.sh", "scripts/dev.sh")


def _load_python(path: Path, name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_hook() -> ModuleType:
    return _load_python(HOOK, "docker_boundary")


def _mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def validate_skill() -> list[str]:
    errors: list[str] = []
    path = ROOT / ".agents" / "skills" / "jobseeker-milestone" / "SKILL.md"
    if not path.is_file():
        return ["required jobseeker-milestone skill is missing"]
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "name: jobseeker-milestone" not in text:
        errors.append("jobseeker-milestone skill lacks valid frontmatter")
    for phrase in (
        "Select the milestone",
        "Plan with independent context",
        "Implement the vertical slice",
        "Prove acceptance",
        "Complete, repair, or block",
        "clean checkout",
        "independent",
        "probable root cause",
        "policy-safe possible fixes",
        "preferred fix",
        "exact Docker commands",
        "repair-and-rerun loop",
        "user-owned input",
        "security, privacy, or compliance",
        "read-only diagnostics",
    ):
        if phrase.lower() not in text.lower():
            errors.append(f"jobseeker-milestone skill lacks {phrase!r}")

    agents_text = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    for phrase in (
        "probable root cause",
        "policy-safe possible fixes",
        "preferred fix",
        "repair loop",
        "user-owned input",
        "security, privacy, or compliance",
        "read-only diagnostics",
    ):
        if phrase.lower() not in agents_text.lower():
            errors.append(f"AGENTS.md lacks blocker guidance {phrase!r}")

    interface_path = path.parent / "agents" / "openai.yaml"
    try:
        interface = _mapping(yaml.safe_load(interface_path.read_text(encoding="utf-8")))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"invalid jobseeker-milestone agents/openai.yaml: {exc}")
    else:
        default_prompt = _mapping(interface.get("interface")).get("default_prompt")
        if not isinstance(default_prompt, str):
            errors.append("jobseeker-milestone interface lacks a default prompt")
        else:
            for phrase in (
                "$jobseeker-milestone",
                "repair and rerun",
                "user input",
                "security",
                "privacy",
                "compliance",
            ):
                if phrase.lower() not in default_prompt.lower():
                    errors.append(
                        "jobseeker-milestone default prompt lacks "
                        f"{phrase!r}"
                    )

    prompt_paths = sorted((ROOT / "docs" / "prompts").glob("[0-2][0-9]-*.md"))
    if len(prompt_paths) != 23:
        errors.append("numbered prompt set must contain exactly 23 files")
    for prompt_path in prompt_paths:
        prompt_text = prompt_path.read_text(encoding="utf-8").lower()
        for phrase in (
            "repair-loop inputs",
            "rerun invalidated gates",
            "user-owned input",
            "security, privacy, or compliance",
        ):
            if phrase not in prompt_text:
                errors.append(
                    f"{prompt_path.relative_to(ROOT)} lacks workflow rule {phrase!r}"
                )
        if "sets the milestone to `blocked` and stops the full pipeline" in prompt_text:
            errors.append(
                f"{prompt_path.relative_to(ROOT)} retains obsolete stop-on-failure policy"
            )
    return errors


def validate_agents() -> list[str]:
    errors: list[str] = []
    folder = ROOT / ".codex" / "agents"
    actual = {path.stem for path in folder.glob("*.toml")}
    missing = sorted(set(AGENT_SPECS) - actual)
    if missing:
        errors.append(f"missing named agents: {', '.join(missing)}")
    for name, sandbox in AGENT_SPECS.items():
        path = folder / f"{name}.toml"
        if not path.is_file():
            continue
        try:
            data = tomllib.loads(path.read_text(encoding="utf-8"))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"invalid agent TOML {path.relative_to(ROOT)}: {exc}")
            continue
        if data.get("name") != name:
            errors.append(f"agent {name} has a mismatched name")
        if data.get("sandbox_mode") != sandbox:
            errors.append(f"agent {name} must use sandbox_mode={sandbox}")
        instructions = data.get("developer_instructions")
        if not isinstance(instructions, str) or len(instructions.strip()) < 100:
            errors.append(f"agent {name} lacks bounded developer instructions")
    return errors


def validate_config_and_rules() -> list[str]:
    errors: list[str] = []
    config_path = ROOT / ".codex" / "config.toml"
    rules_path = ROOT / ".codex" / "rules" / "default.rules"
    try:
        config = tomllib.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        return [f"invalid .codex/config.toml: {exc}"]
    features = _mapping(config.get("features"))
    if any(features.get(name) is not True for name in ("hooks", "multi_agent")):
        errors.append("Codex config must enable hooks and multi_agent")
    agents = _mapping(config.get("agents"))
    if agents.get("max_threads") != 4 or agents.get("max_depth") != 1:
        errors.append("Codex config must bound agents to four threads and one level")
    try:
        rules = re.sub(r"\s+", "", rules_path.read_text(encoding="utf-8"))
    except OSError as exc:
        return errors + [f"cannot read .codex/rules/default.rules: {exc}"]
    required_rules = (
        'pattern=["git","reset","--hard"]',
        'pattern=["git","clean"]',
        'pattern=["git","push",["--force","-f"]]',
        'pattern=["docker","compose","down","-v"]',
        'pattern=["docker","compose","--profile","dev","down","-v"]',
        'pattern=["docker","system","prune"]',
        'pattern=["docker","volume","rm"]',
        'pattern=["docker","compose","--profile","live"]',
    )
    for pattern in required_rules:
        if pattern not in rules:
            errors.append(f"Codex rules lack required guard {pattern}")
    return errors


def validate_hooks() -> list[str]:
    errors: list[str] = []
    path = ROOT / ".codex" / "hooks.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid .codex/hooks.json: {exc}"]
    hooks = _mapping(data.get("hooks"))
    pre = hooks.get("PreToolUse")
    stop = hooks.get("Stop")
    if not isinstance(pre, list) or not pre:
        errors.append("Codex hooks lack PreToolUse enforcement")
    elif "enforce_docker_boundary.py" not in json.dumps(pre):
        errors.append("PreToolUse does not invoke the Docker-boundary hook")
    if not isinstance(stop, list) or not stop:
        errors.append("Codex hooks lack Stop enforcement")
    elif "validate_completion.py" not in json.dumps(stop):
        errors.append("Stop does not invoke the completion hook")
    for hook_path in (HOOK, ROOT / ".codex" / "hooks" / "validate_completion.py"):
        if not hook_path.is_file():
            errors.append(f"missing hook: {hook_path.relative_to(ROOT)}")
    return errors


def validate_wrappers() -> list[str]:
    errors: list[str] = []
    for relative in WRAPPERS:
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"missing Docker wrapper: {relative}")
            continue
        for number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#!") or line == "set -euo pipefail":
                continue
            if line.startswith("exec "):
                line = line.removeprefix("exec ")
            if not line.startswith("docker compose "):
                errors.append(f"{relative}:{number} is not Docker Compose orchestration")
    makefile = ROOT / "Makefile"
    for number, line in enumerate(makefile.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("\t"):
            continue
        recipe = line.strip().removeprefix("@")
        if not recipe.startswith("docker compose "):
            errors.append(f"Makefile:{number} is not Docker Compose orchestration")
    return errors


def validate_tooling_configuration() -> list[str]:
    errors: list[str] = []
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    optional = _mapping(_mapping(pyproject.get("project")).get("optional-dependencies"))
    dev = optional.get("dev")
    dependencies = " ".join(dev) if isinstance(dev, list) else ""
    for tool in ("pytest", "ruff", "mypy", "pre-commit"):
        if tool not in dependencies:
            errors.append(f"tooling image dependency set lacks {tool}")
    mypy = _mapping(_mapping(pyproject.get("tool")).get("mypy"))
    if "ignore_errors" in mypy:
        errors.append("mypy may not set global ignore_errors")
    precommit = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    repos = _mapping(precommit).get("repos")
    if (
        not isinstance(repos, list)
        or not repos
        or any(not isinstance(repo, dict) or repo.get("repo") != "local" for repo in repos)
    ):
        errors.append("pre-commit must use repository-local hooks only")
    compose = yaml.safe_load((ROOT / "compose.yaml").read_text(encoding="utf-8"))
    services = _mapping(_mapping(compose).get("services"))
    for service in ("api", "worker", "scheduler"):
        env_file = _mapping(services.get(service)).get("env_file")
        if not isinstance(env_file, list) or not any(
            isinstance(item, dict) and item.get("path") == ".env" and item.get("required") is False
            for item in env_file
        ):
            errors.append(f"Compose service {service} must treat .env as an optional override")
    return errors


def validate_evidence_automation() -> list[str]:
    errors: list[str] = []
    runner = ROOT / "scripts" / "run_milestone_00_gates.sh"
    generator = ROOT / "scripts" / "generate_milestone_00_receipt.py"
    if not runner.is_file():
        errors.append("Milestone 00 machine-capture runner is missing")
    else:
        text = runner.read_text(encoding="utf-8")
        for phrase in (
            "git rev-parse HEAD",
            "docker compose --profile dev config --quiet",
            "docker compose --profile dev build api",
            "python scripts/validate_docs.py",
            "python scripts/validate_milestone.py --all",
            "python scripts/validate_codex_controls.py",
            "ruff check .",
            "mypy src",
            "pytest -q",
            "pre-commit run --all-files",
            "manifest.tsv",
            "metadata.tsv",
        ):
            if phrase not in text:
                errors.append(f"Milestone 00 runner lacks {phrase!r}")
    if not generator.is_file():
        errors.append("Milestone 00 receipt generator is missing")
    else:
        text = generator.read_text(encoding="utf-8")
        for phrase in (
            "--main-manifest",
            "--clean-manifest",
            "--policy-review",
            "--evidence-review",
            "M00_PLACEHOLDER_SCOPE",
            "Application behavior owned by Milestones 01-22",
        ):
            if phrase not in text:
                errors.append(f"Milestone 00 receipt generator lacks {phrase!r}")
    return errors


def validate_boundary_cases() -> list[str]:
    errors: list[str] = []
    hook = load_hook()
    denied = {
        "pytest -q": "pytest",
        "python -m pytest": "python",
        "env MODE=test ruff check .": "ruff",
        "command mypy src": "mypy",
        "bash -c 'pytest -q'": "pytest",
        "echo ok && sh -c 'python scripts/validate_docs.py'": "python",
        "echo $(pytest -q)": "pytest",
        "find . -exec python -m pytest {} ;": "python",
        "printf '%s\\n' test | xargs ruff check": "ruff",
        "docker run --rm job-agent pytest": "docker run",
        "docker --context remote run --rm job-agent pytest": "docker run",
        "docker --host unix:///tmp/docker.sock exec api pytest": "docker exec",
        "docker --context remote build .": "docker build",
        "docker container run --rm job-agent pytest": "docker container run",
        "docker container exec api pytest": "docker container exec",
        "docker buildx build .": "docker buildx build",
        "./scripts/not-approved.sh": "scripts/not-approved.sh",
        "make db-reset": "make",
        "make unknown-target": "make",
    }
    for command, expected in denied.items():
        actual = hook.blocked_segment(command)
        if actual != expected:
            errors.append(f"{command!r}: expected denial {expected!r}, got {actual!r}")
    allowed = (
        "docker compose --profile dev run --rm api pytest -q",
        "docker --context local compose --profile dev build api",
        "docker compose --profile dev run --rm api sh -c 'pytest -q'",
        "git status --short",
        "sed -n '/pytest/p' pyproject.toml",
        "rg 'python|pytest' docs",
        "echo 'pytest -q is documented text'",
        "./scripts/check.sh",
        "bash scripts/bootstrap.sh",
        "bash scripts/run_milestone_00_gates.sh --run-label clean",
        "bash scripts/run_milestone_03_gates.sh --run-label clean",
        "make lint",
    )
    for command in allowed:
        if hook.blocked_segment(command) is not None:
            errors.append(f"allowed command was blocked: {command!r}")
    if "db-reset" in hook.APPROVED_MAKE_TARGETS:
        errors.append("destructive Make target db-reset must not be approved by the Docker boundary")
    return errors


def main() -> int:
    errors: list[str] = []
    for validation in (
        validate_skill,
        validate_agents,
        validate_config_and_rules,
        validate_hooks,
        validate_wrappers,
        validate_tooling_configuration,
        validate_evidence_automation,
        validate_boundary_cases,
    ):
        try:
            errors.extend(validation())
        except (OSError, RuntimeError, tomllib.TOMLDecodeError, yaml.YAMLError) as exc:
            errors.append(f"{validation.__name__} failed: {exc}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Codex control validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
