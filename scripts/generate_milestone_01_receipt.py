#!/usr/bin/env python3
"""Generate Milestone 01 evidence from machine captures and independent reviews."""

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


ACCEPTANCE_IDS = tuple(f"M01-AC{number:02d}" for number in range(1, 5))
PLACEHOLDER_SCOPE = (
    "README.md",
    "docs/PROJECT_CHARTER.md",
    "docs/milestones/01-project-charter-and-scope.md",
    "docs/prompts/01-project-charter-and-scope.md",
    "docs/adr/0001-human-in-the-loop-boundary.md",
    "docs/adr/0002-local-first-mvp.md",
    "scripts/validate_docs.py",
    "scripts/generate_milestone_01_receipt.py",
    "tests/test_charter_contract.py",
    "tests/test_milestone_01_evidence.py",
)
LIMITATION = (
    "Jobicy, Remote OK, and OpenAI are conditional integration goals, not permission or "
    "operational evidence; Milestones 02, 08, and 10 must validate their exact policies, "
    "configuration, credentials, and bounded live smokes."
)


def read_reviews(
    root: Path, policy_value: str | Path, evidence_value: str | Path
) -> tuple[dict[str, Any], dict[str, list[str]], list[str]]:
    """Validate independent policy and acceptance-review artifacts."""
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
        raise EvidenceError("evidence analyst review lacks the exact M01 acceptance set")
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
    """Return unfinished implementation markers in the M01 acceptance scope."""
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
    parser.add_argument("--output", default="artifacts/verification/milestone-01.json")
    parser.add_argument(
        "--placeholder-log",
        default="artifacts/verification/milestone-01-placeholder-scan.log",
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
            "scope=M01 charter, ADR, documentation validation, and evidence tooling\n"
            + ("result=PASS\n" if not findings else "result=FAIL\n")
            + "\n".join(findings)
            + ("\n" if findings else ""),
            encoding="utf-8",
        )
        if findings:
            raise EvidenceError("M01 placeholder scan failed: " + ", ".join(findings))

        main_logs = {item["gate_id"]: item["log_refs"][0] for item in main_commands}
        docs = {
            "charter": "docs/PROJECT_CHARTER.md",
            "demo": "docs/DEMO_ACCEPTANCE.md",
            "milestone": "docs/milestones/01-project-charter-and-scope.md",
            "prompt": "docs/prompts/01-project-charter-and-scope.md",
            "adr1": "docs/adr/0001-human-in-the-loop-boundary.md",
            "adr2": "docs/adr/0002-local-first-mvp.md",
            "readme": "README.md",
            "validator": "scripts/validate_docs.py",
            "tests": "tests/test_charter_contract.py",
        }
        for label, reference in docs.items():
            repository_file(ROOT, reference, f"M01 {label}")
        mapping = {
            "M01-AC01": [
                docs["charter"],
                docs["demo"],
                docs["validator"],
                docs["tests"],
                main_logs["04-validate-docs"],
                main_logs["09-pytest"],
            ],
            "M01-AC02": [
                docs["charter"],
                docs["adr1"],
                docs["readme"],
                docs["validator"],
                main_logs["09-pytest"],
            ],
            "M01-AC03": [
                docs["charter"],
                docs["adr2"],
                docs["readme"],
                main_logs["01-compose-config"],
                main_logs["02-build-api"],
                *clean_refs,
            ],
            "M01-AC04": [
                docs["milestone"],
                docs["prompt"],
                docs["validator"],
                *main_refs,
                *clean_refs,
                *evidence_review_refs,
                *review["references"],
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
            "milestone": "01",
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
            "known_limitations": [LIMITATION],
        }
        output, _ = output_file(ROOT, args.output, "receipt output")
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        temporary.replace(output)
    except (EvidenceError, OSError, tokenize.TokenError) as exc:
        print(f"ERROR: {exc}")
        return 1
    print(f"generated {args.output} from validated machine evidence")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
