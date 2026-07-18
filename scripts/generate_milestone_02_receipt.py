#!/usr/bin/env python3
"""Generate Milestone 02 evidence from machine captures and independent reviews."""

from __future__ import annotations

import argparse
import ast
import io
import json
from pathlib import Path
import re
import tokenize
from typing import Any

from generate_milestone_00_receipt import (
    ROOT,
    EvidenceError,
    checked_references,
    output_file,
    read_json_object,
    read_manifest,
    repository_file,
    unique,
)


ACCEPTANCE_IDS = tuple(f"M02-AC{number:02d}" for number in range(1, 6))
PLACEHOLDER_SCOPE = (
    "config/platform_policy.yaml",
    "config/platform_policy.example.yaml",
    "docs/PLATFORM_AUDIT.md",
    "docs/milestones/02-compliance-and-platform-policy-registry.md",
    "docs/prompts/02-compliance-and-platform-policy-registry.md",
    "src/job_agent/policy/models.py",
    "src/job_agent/policy/service.py",
    "src/job_agent/policy/exceptions.py",
    "src/job_agent/cli.py",
    "tests/test_policy.py",
    "tests/test_cli.py",
    "scripts/generate_milestone_02_receipt.py",
    "tests/test_milestone_02_evidence.py",
)


def read_reviews(
    root: Path, policy_value: str | Path, evidence_value: str | Path
) -> tuple[dict[str, Any], dict[str, list[str]], list[str]]:
    """Require independent GO/PASS artifacts for the exact M02 acceptance set."""
    policy, policy_ref = read_json_object(root, policy_value, "policy/release review")
    if policy.get("verdict") != "GO" or policy.get("unresolved_high_critical") != []:
        raise EvidenceError("policy/release review is not an unqualified GO")
    reviewer = policy.get("reviewer")
    if not isinstance(reviewer, str) or not reviewer.strip():
        raise EvidenceError("policy/release review has no reviewer")
    policy_refs = checked_references(root, policy.get("references"), "policy/release review")

    evidence, evidence_ref = read_json_object(root, evidence_value, "evidence analyst review")
    if evidence.get("result") != "PASS":
        raise EvidenceError("evidence analyst review did not PASS")
    acceptance = evidence.get("acceptance")
    if not isinstance(acceptance, dict) or set(acceptance) != set(ACCEPTANCE_IDS):
        raise EvidenceError("evidence analyst review lacks the exact M02 acceptance set")
    evidence_refs: dict[str, list[str]] = {}
    for acceptance_id in ACCEPTANCE_IDS:
        item = acceptance[acceptance_id]
        if not isinstance(item, dict) or item.get("result") != "PASS":
            raise EvidenceError(f"evidence analyst did not PASS {acceptance_id}")
        evidence_refs[acceptance_id] = checked_references(
            root, item.get("references"), f"evidence analyst {acceptance_id}"
        )
    review = {
        "verdict": "GO",
        "reviewer": reviewer,
        "references": sorted(set([policy_ref, *policy_refs])),
        "unresolved_high_critical": [],
    }
    return review, evidence_refs, [evidence_ref]


def placeholder_findings(root: Path) -> list[str]:
    """Find unfinished implementation markers in the M02 acceptance scope."""
    findings: list[str] = []
    marker = re.compile(r"\b(?:TODO|FIXME|TBD)\b", re.IGNORECASE)
    for relative in PLACEHOLDER_SCOPE:
        path = root / relative
        if not path.is_file():
            findings.append(f"missing:{relative}")
            continue
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".py":
            try:
                tree = ast.parse(text, filename=relative)
            except SyntaxError as exc:
                findings.append(f"syntax:{relative}:{exc.lineno}")
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
                    function = node.exc.func
                    if isinstance(function, ast.Name) and function.id == "NotImplementedError":
                        findings.append(f"not-implemented:{relative}:{node.lineno}")
            for token in tokenize.generate_tokens(io.StringIO(text).readline):
                if token.type == tokenize.COMMENT and marker.search(token.string):
                    findings.append(f"unfinished-comment:{relative}:{token.start[0]}")
        else:
            for line_number, line in enumerate(text.splitlines(), start=1):
                if marker.search(line):
                    findings.append(f"unfinished-marker:{relative}:{line_number}")
    return findings


def read_clean_checkout(root: Path, manifest_value: str | Path) -> str:
    """Require a machine-captured empty Git status beside the clean manifest."""
    manifest, _ = repository_file(root, manifest_value, "clean manifest")
    status_path = manifest.with_name("checkout-status.log")
    status_path, status_ref = repository_file(root, status_path, "clean checkout status")
    if status_path.read_text(encoding="utf-8") != "":
        raise EvidenceError("clean checkout status is not empty")
    return status_ref


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--main-manifest", required=True)
    parser.add_argument("--clean-manifest", required=True)
    parser.add_argument("--policy-review", required=True)
    parser.add_argument("--evidence-review", required=True)
    parser.add_argument("--output", default="artifacts/verification/milestone-02.json")
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-02-placeholder-scan.log",
    )
    args = parser.parse_args()

    try:
        main_metadata, main_commands, main_refs = read_manifest(
            ROOT, args.main_manifest, "main"
        )
        clean_metadata, clean_commands, clean_refs = read_manifest(
            ROOT, args.clean_manifest, "clean"
        )
        clean_status_ref = read_clean_checkout(ROOT, args.clean_manifest)
        clean_refs = [*clean_refs, clean_status_ref]
        if main_metadata["tested_commit"] != clean_metadata["tested_commit"]:
            raise EvidenceError("main and clean runs tested different commits")
        review, evidence_refs, evidence_review_refs = read_reviews(
            ROOT, args.policy_review, args.evidence_review
        )

        findings = placeholder_findings(ROOT)
        placeholder_path, placeholder_ref = output_file(
            ROOT, args.placeholder_log, "placeholder log"
        )
        placeholder_path.write_text(
            "scope=M02 policy registry, enforcement, CLI, audit, tests, and evidence tooling\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M02 placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        required = {
            "policy": "config/platform_policy.yaml",
            "example": "config/platform_policy.example.yaml",
            "audit": "docs/PLATFORM_AUDIT.md",
            "milestone": "docs/milestones/02-compliance-and-platform-policy-registry.md",
            "models": "src/job_agent/policy/models.py",
            "service": "src/job_agent/policy/service.py",
            "cli": "src/job_agent/cli.py",
            "tests": "tests/test_policy.py",
            "cli_tests": "tests/test_cli.py",
        }
        for label, reference in required.items():
            repository_file(ROOT, reference, f"M02 {label}")
        mapping = {
            "M02-AC01": [
                required["policy"], required["example"], required["models"],
                required["tests"], main_logs["09-pytest"],
            ],
            "M02-AC02": [
                required["service"], required["tests"], main_logs["09-pytest"],
            ],
            "M02-AC03": [
                required["service"], required["tests"], main_logs["09-pytest"],
            ],
            "M02-AC04": [
                required["policy"], required["audit"], required["milestone"],
                main_logs["04-validate-docs"], *review["references"],
            ],
            "M02-AC05": [
                required["cli"], required["cli_tests"], required["service"],
                *main_refs, *clean_refs, *evidence_review_refs,
            ],
        }
        acceptance = {
            acceptance_id: {
                "result": "PASS",
                "references": unique(
                    [*mapping[acceptance_id], *evidence_refs[acceptance_id]]
                ),
            }
            for acceptance_id in ACCEPTANCE_IDS
        }
        receipt = {
            "milestone": "02",
            "tested_commit": main_metadata["tested_commit"],
            "timestamp_utc": main_metadata["timestamp_utc"],
            "image_digest": main_metadata["image_digest"],
            "result": "PASS",
            "commands": [*main_commands, *clean_commands],
            "acceptance": acceptance,
            "review": review,
            "clean_checkout": {"result": "PASS", "references": unique(clean_refs)},
            "placeholders": {
                "result": "PASS",
                "matches": [],
                "references": [placeholder_ref],
                "scope": list(PLACEHOLDER_SCOPE),
            },
            "known_limitations": [
                "All live reads and marketplace writes remain disabled; Milestone 08 "
                "must obtain explicit owner approval and prove bounded source reads."
            ],
        }
        output, _ = output_file(ROOT, args.output, "receipt output")
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    except (EvidenceError, KeyError, OSError, tokenize.TokenError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"generated {args.output} from validated machine evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
