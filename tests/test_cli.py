from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from job_agent.cli import main
from job_agent.policy.models import PolicyAction
from job_agent.profile import ProfileBundleService


def _write_policy(path: Path, discover: str) -> None:
    actions = {action.value: "disabled" for action in PolicyAction}
    actions["discover"] = discover
    payload = {
        "version": "cli-test",
        "platforms": [
            {
                "platform_id": "synthetic",
                "display_name": "Synthetic",
                "reviewed_at": "2026-01-01",
                "review_due_at": "2099-01-01",
                "terms_url": "https://example.test/terms",
                "help_or_api_url": "https://example.test/api",
                "owner_approved": discover == "public_feed",
                "actions": actions,
                "limits": {
                    "requests_per_minute": 1 if discover == "public_feed" else 0,
                    "retention_days": 30,
                },
                "notes": "CLI synthetic registry.",
            }
        ],
    }
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_policy_check_prints_allowed_structured_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "policy.json"
    _write_policy(path, "public_feed")
    assert (
        main(
            ["policy", "check", "synthetic", "discover", "--network", "--action-id", "cli-1"],
            policy_path=path,
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert payload["allowed"] is True
    assert payload["reason_code"] == "allowed"
    assert payload["action_id"] == "cli-1"


def test_policy_check_denial_is_json_and_exit_two(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "policy.json"
    _write_policy(path, "manual_only")
    assert main(["policy", "check", "synthetic", "discover", "--network"], policy_path=path) == 2
    payload = json.loads(capsys.readouterr().out)
    assert payload["allowed"] is False
    assert payload["reason_code"] == "manual_network_denied"


def test_policy_configuration_failure_is_safe_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "policy.json"
    path.write_text('{"secret": "must-not-leak"}', encoding="utf-8")
    assert main(["policy", "check", "synthetic", "discover"], policy_path=path) == 3
    output = capsys.readouterr().out
    assert json.loads(output)["error"]["code"] == "policy_configuration_invalid"
    assert "must-not-leak" not in output


def test_sources_list_reports_manual_capture(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["sources", "list"]) == 0
    assert capsys.readouterr().out.splitlines() == ["manual"]


def test_profile_validate_reports_structured_counts(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(["profile-validate"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["valid"] is True
    assert payload["counts"]["services"] > 0
    assert payload["counts"]["evidence_records"] > 0
    assert payload["counts"]["proposal_eligible_claims"] > 0
    assert payload["counts"]["metrics"] > 0


def test_profile_validate_failure_is_safe_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("private_value: must-not-leak\n", encoding="utf-8")
    assert (
        main(
            [
                "profile-validate",
                "--profile",
                str(invalid),
                "--scoring",
                str(invalid),
                "--manifest",
                str(invalid),
            ]
        )
        == 3
    )
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["valid"] is False
    assert payload["error"]["code"] == "profile_configuration_invalid"
    assert "must-not-leak" not in output


def test_profile_validate_unsupported_version_fails_with_safe_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    bundle = ProfileBundleService.from_yaml().bundle.model_dump(mode="json")
    bundle["profile"]["schema_version"] = "2.0"
    bundle["profile"]["identity"]["display_name"] = "must-not-leak"
    paths = {
        section: tmp_path / f"{section}.yaml"
        for section in ("profile", "scoring", "manifest")
    }
    for section, path in paths.items():
        path.write_text(yaml.safe_dump(bundle[section]), encoding="utf-8")

    assert (
        main(
            [
                "profile-validate",
                "--profile",
                str(paths["profile"]),
                "--scoring",
                str(paths["scoring"]),
                "--manifest",
                str(paths["manifest"]),
            ]
        )
        == 3
    )
    output = capsys.readouterr().out
    payload = json.loads(output)
    assert payload["valid"] is False
    assert payload["error"]["code"] == "profile_configuration_invalid"
    assert "must-not-leak" not in output
    assert str(tmp_path) not in output
