#!/usr/bin/env python3
"""Deny host-native application toolchain commands before Codex runs them."""

from __future__ import annotations

import json
from pathlib import PurePosixPath
import re
import shlex
import sys


DENIED = {
    "alembic",
    "celery",
    "job-agent",
    "mypy",
    "pip",
    "pip3",
    "pre-commit",
    "pytest",
    "python",
    "python3",
    "ruff",
    "uv",
    "uvicorn",
}
SHELLS = {"bash", "dash", "sh", "zsh"}
WRAPPERS = {"command", "exec", "nohup", "sudo"}
APPROVED_SHELL_WRAPPERS = {
    "scripts/bootstrap.sh",
    "scripts/check.sh",
    "scripts/dev.sh",
    "scripts/run_milestone_00_gates.sh",
}
APPROVED_MAKE_TARGETS = {
    "bootstrap",
    "check",
    "db-reset",
    "down",
    "eval",
    "lint",
    "migrate",
    "pre-commit",
    "release-check",
    "seed",
    "test",
    "test-integration",
    "type",
    "up",
}
CONTROL = {"&&", "||", ";", "|", "&", "(", ")"}
ASSIGNMENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=.*", re.DOTALL)


def _basename(word: str) -> str:
    return PurePosixPath(word).name


def _shell_tokens(command: str) -> list[str]:
    lexer = shlex.shlex(command, posix=True, punctuation_chars=";&|()")
    lexer.whitespace_split = True
    lexer.commenters = ""
    return list(lexer)


def _segments(command: str) -> list[list[str]]:
    try:
        tokens = _shell_tokens(command)
    except ValueError:
        # An incomplete shell construct is not safe to treat as an allowed command.
        return [["__invalid_shell__"]]
    result: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in CONTROL:
            if current:
                result.append(current)
                current = []
        else:
            current.append(token)
    if current:
        result.append(current)
    return result


def _command_substitutions(command: str) -> list[str]:
    """Return executable substitutions, ignoring literal text in single quotes."""
    found: list[str] = []
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            escaped = False
            index += 1
            continue
        if char == "\\" and quote != "'":
            escaped = True
            index += 1
            continue
        if char in {"'", '"'}:
            if quote is None:
                quote = char
            elif quote == char:
                quote = None
            index += 1
            continue
        if quote == "'":
            index += 1
            continue
        if char == "`":
            end = command.find("`", index + 1)
            if end < 0:
                found.append("__invalid_shell__")
                break
            found.append(command[index + 1 : end])
            index = end + 1
            continue
        marker_length = 0
        if command.startswith("$(", index):
            marker_length = 2
        elif command.startswith("<(", index) or command.startswith(">(", index):
            marker_length = 2
        if marker_length:
            depth = 1
            cursor = index + marker_length
            inner_quote: str | None = None
            while cursor < len(command) and depth:
                inner = command[cursor]
                if inner in {"'", '"'}:
                    if inner_quote is None:
                        inner_quote = inner
                    elif inner_quote == inner:
                        inner_quote = None
                elif inner_quote != "'" and inner == "(":
                    depth += 1
                elif inner_quote != "'" and inner == ")":
                    depth -= 1
                cursor += 1
            if depth:
                found.append("__invalid_shell__")
                break
            found.append(command[index + marker_length : cursor - 1])
            index = cursor
            continue
        index += 1
    return found


def _strip_prefixes(words: list[str]) -> list[str]:
    remaining = list(words)
    while remaining and ASSIGNMENT.fullmatch(remaining[0]):
        remaining.pop(0)
    return remaining


def _docker_arguments(words: list[str]) -> list[str]:
    """Remove Docker global options while retaining the actual subcommand."""
    remaining = list(words)
    options_with_values = {
        "--config",
        "--context",
        "--host",
        "--log-level",
        "-c",
        "-H",
        "-l",
    }
    while remaining and remaining[0].startswith("-"):
        option = remaining.pop(0)
        if "=" not in option and option in options_with_values:
            if not remaining:
                return []
            remaining.pop(0)
    return remaining


def _blocked_words(words: list[str]) -> str | None:
    words = _strip_prefixes(words)
    if not words:
        return None
    executable = _basename(words[0])
    if executable == "__invalid_shell__":
        return "invalid shell command"
    if executable == "env":
        remaining = words[1:]
        while remaining and (remaining[0].startswith("-") or ASSIGNMENT.fullmatch(remaining[0])):
            remaining.pop(0)
        return _blocked_words(remaining)
    if executable in WRAPPERS:
        remaining = words[1:]
        while remaining and remaining[0].startswith("-"):
            remaining.pop(0)
        return _blocked_words(remaining)
    if executable in {"nice", "time", "timeout"}:
        remaining = words[1:]
        while remaining and (remaining[0].startswith("-") or remaining[0].replace(".", "").isdigit()):
            remaining.pop(0)
        return _blocked_words(remaining)
    if executable == "xargs":
        for position, word in enumerate(words[1:], start=1):
            blocked = _blocked_words(words[position:])
            if blocked:
                return blocked
            if not word.startswith("-"):
                break
        return None
    if executable == "find":
        for marker in ("-exec", "-execdir", "-ok", "-okdir"):
            if marker in words:
                position = words.index(marker)
                blocked = _blocked_words(words[position + 1 :])
                if blocked:
                    return blocked
        return None
    if executable == "docker":
        remaining = _docker_arguments(words[1:])
        if remaining and remaining[0] == "compose":
            return None
        if remaining and remaining[0] in {"build", "exec", "run"}:
            return f"docker {remaining[0]}"
        if len(remaining) > 1 and remaining[0] == "container" and remaining[1] in {
            "exec",
            "run",
        }:
            return f"docker container {remaining[1]}"
        if len(remaining) > 1 and remaining[0] == "buildx" and remaining[1] == "build":
            return "docker buildx build"
        return None
    if executable == "docker-compose":
        return None
    if executable in DENIED:
        return executable
    if executable in SHELLS:
        remaining = words[1:]
        if "-c" in remaining:
            position = remaining.index("-c")
            if position + 1 >= len(remaining):
                return executable
            return blocked_segment(remaining[position + 1])
        scripts = [word.removeprefix("./") for word in remaining if not word.startswith("-")]
        if scripts and scripts[0] in APPROVED_SHELL_WRAPPERS:
            return None
        return executable
    normalized = words[0].removeprefix("./")
    if normalized.endswith(".sh") and normalized not in APPROVED_SHELL_WRAPPERS:
        return normalized
    if executable == "make":
        targets = [word for word in words[1:] if not word.startswith("-") and "=" not in word]
        if any(target not in APPROVED_MAKE_TARGETS for target in targets):
            return "make"
    return None


def executable(segment: str) -> str:
    """Return the effective first executable for compatibility with older checks."""
    segments = _segments(segment)
    if not segments:
        return ""
    words = _strip_prefixes(segments[0])
    return words[0] if words else ""


def blocked_segment(command: str) -> str | None:
    """Return the first denied executable in a shell command, if any."""
    for substitution in _command_substitutions(command):
        blocked = blocked_segment(substitution)
        if blocked:
            return blocked
    for words in _segments(command):
        blocked = _blocked_words(words)
        if blocked:
            return blocked
    return None


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    tool_input = payload.get("tool_input") or {}
    command = str(tool_input.get("command") or tool_input.get("cmd") or "")
    denied = blocked_segment(command)
    if denied:
        result = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"Host-native '{denied}' is blocked. Run application builds, "
                    "dependencies, Python, tests, migrations, and checks through "
                    "docker compose."
                ),
            }
        }
        print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
