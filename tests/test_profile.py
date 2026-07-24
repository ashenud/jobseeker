from __future__ import annotations

from pathlib import Path
import subprocess
from typing import Any

from pydantic import ValidationError
import pytest
import yaml

from job_agent.profile import (
    EvidenceClassification,
    ProfileBundle,
    ProfileBundleService,
    ProfileConfig,
    ProfileConfigurationError,
    PortfolioManifest,
    ScoringConfig,
)


def _canonical_data() -> dict[str, Any]:
    service = ProfileBundleService.from_yaml()
    return service.bundle.model_dump(mode="json")


def test_canonical_bundle_resolves_claims_and_returns_sanitized_summary() -> None:
    service = ProfileBundleService.from_yaml()
    summary = service.validation_summary()

    assert summary == {
        "result": "PASS",
        "schema_versions": {
            "profile": "1.0",
            "scoring": "1.0",
            "portfolio_manifest": "1.0",
        },
        "counts": {
            "services": 12,
            "evidence_records": 1,
            "proposal_eligible_claims": 8,
            "metrics": 18,
        },
        "dangling_evidence_ids": [],
        "ineligible_evidence_ids": [],
        "contradictions": [],
    }

    record = service.bundle.manifest.records[0]
    assert record.evidence_id == "herbacorium_amazon_content"
    assert record.classification == EvidenceClassification.completed_client_work
    assert record.proposal_eligible is True
    assert record.source_files_allowed is False
    assert record.performance_claims_allowed is False
    assert {claim.text for claim in service.bundle.profile.claims} == set(record.safe_claims)


def test_owner_constraints_are_explicit_and_global_floor_overrides_small_task_range() -> None:
    profile = ProfileBundleService.from_yaml().bundle.profile
    constraints = profile.constraints
    service_budgets = {
        service.service_id: service.minimum_project_budget_usd for service in profile.services
    }

    assert constraints.minimum_hourly_rate_usd == 15
    assert constraints.target_hourly_rate_usd == 25
    assert constraints.global_minimum_project_budget_usd == 100
    assert service_budgets["small_graphic_design"] == 100
    assert service_budgets["amazon_ecommerce_creative"] == 250
    assert service_budgets["monthly_retainer"] == 1500
    assert constraints.workload.maximum_reviews_per_day == 100
    assert constraints.workload.targeted_applications_per_day == 15
    assert constraints.workload.maximum_applications_per_day == 20
    assert constraints.working_hours_overlap.minimum_hours_per_working_day == 3
    assert constraints.working_hours_overlap.preferred_hours_per_working_day == 4
    assert constraints.unpaid_tests.maximum_unpaid_skill_assessment_minutes == 30
    assert constraints.unpaid_tests.substantial_or_client_ready_work_must_be_paid
    assert constraints.geography.strict_geographic_exclusions == ()


def test_canonical_digit_leading_service_id_resolves_in_profile_and_evidence() -> None:
    bundle = ProfileBundleService.from_yaml().bundle
    assert "3d_product_visualization" in {
        service.service_id for service in bundle.profile.services
    }
    assert "3d_product_visualization" in bundle.manifest.records[0].supported_service_ids


def test_digit_leading_service_id_validates_across_profile_and_manifest() -> None:
    data = _canonical_data()
    existing_id = data["profile"]["services"][0]["service_id"]
    data["profile"]["services"][0]["service_id"] = "2d_graphic_design"
    for record in data["manifest"]["records"]:
        record["supported_service_ids"] = [
            "2d_graphic_design" if value == existing_id else value
            for value in record["supported_service_ids"]
        ]

    bundle = ProfileBundle.model_validate(data)
    assert bundle.profile.services[0].service_id == "2d_graphic_design"


@pytest.mark.parametrize("service_id", ("_3d", "3-d", "3 d", "3D", ""))
def test_service_ids_reject_invalid_digit_leading_forms(service_id: str) -> None:
    data = _canonical_data()
    data["profile"]["services"][0]["service_id"] = service_id
    with pytest.raises(ValidationError):
        ProfileBundle.model_validate(data)


def test_digit_leading_general_identifier_remains_rejected() -> None:
    data = _canonical_data()
    data["profile"]["claims"][0]["claim_id"] = "3d_claim"
    with pytest.raises(ValidationError):
        ProfileBundle.model_validate(data)


@pytest.mark.parametrize(
    ("model", "path"),
    (
        (ProfileConfig, "config/profile.example.yaml"),
        (ScoringConfig, "config/scoring.example.yaml"),
    ),
)
def test_synthetic_examples_are_strictly_schema_compatible(
    model: type[ProfileConfig] | type[ScoringConfig], path: str
) -> None:
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    parsed = model.model_validate(data)
    assert parsed.schema_version == "1.0"
    assert "Dilshan" not in Path(path).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "mutate",
    (
        lambda data: data["profile"].update(extra="forbidden"),
        lambda data: data["profile"]["identity"].update(timezone="UTC+05:30"),
        lambda data: data["profile"]["identity"].update(
            portfolio_url="https://owner:secret@example.test"
        ),
        lambda data: data["profile"]["services"].append(data["profile"]["services"][0]),
        lambda data: data["profile"]["claims"].append(data["profile"]["claims"][0]),
        lambda data: data["manifest"]["records"].append(data["manifest"]["records"][0]),
        lambda data: data["scoring"]["dimensions"].append(
            data["scoring"]["dimensions"][0]
        ),
        lambda data: data["scoring"]["metrics"].append(data["scoring"]["metrics"][0]),
    ),
)
def test_strict_models_reject_extras_invalid_timezone_credentials_and_duplicate_ids(
    mutate: Any,
) -> None:
    data = _canonical_data()
    mutate(data)
    with pytest.raises(ValidationError):
        ProfileBundle.model_validate(data)


@pytest.mark.parametrize(
    "mutate",
    (
        lambda data: data["profile"]["constraints"].update(target_hourly_rate_usd=14),
        lambda data: data["profile"]["services"][0].update(
            minimum_project_budget_usd=99
        ),
        lambda data: data["profile"]["constraints"]["workload"].update(
            targeted_applications_per_day=21
        ),
        lambda data: data["profile"]["constraints"]["working_hours_overlap"].update(
            preferred_hours_per_working_day=2
        ),
        lambda data: data["scoring"]["rules"].update(minimum_hourly_rate_usd=14),
        lambda data: data["scoring"]["rules"].update(max_applications_per_day=101),
        lambda data: data["scoring"]["thresholds"].update(priority_at_or_above=5.0),
        lambda data: data["scoring"]["dimensions"][0].update(weight=0.25),
    ),
)
def test_rate_budget_cap_overlap_and_scoring_contradictions_fail(mutate: Any) -> None:
    data = _canonical_data()
    mutate(data)
    with pytest.raises(ValidationError):
        ProfileBundle.model_validate(data)


def test_dangling_and_unapproved_claims_fail_cross_file_resolution() -> None:
    dangling = _canonical_data()
    dangling["profile"]["claims"][0]["evidence_ids"] = ("missing_evidence",)
    with pytest.raises(ValidationError, match="dangling evidence"):
        ProfileBundle.model_validate(dangling)

    unsupported = _canonical_data()
    unsupported["profile"]["claims"][0]["text"] = "Increased conversion by 50%."
    with pytest.raises(ValidationError, match="not approved by evidence"):
        ProfileBundle.model_validate(unsupported)


@pytest.mark.parametrize("classification", ("concept", "speculative", "proposal_only"))
def test_non_client_work_cannot_support_completed_work_claims(classification: str) -> None:
    data = _canonical_data()
    record = data["manifest"]["records"][0]
    record["classification"] = classification
    record["completed_work_claim_allowed"] = False
    with pytest.raises(ValidationError, match="completed-work claim"):
        ProfileBundle.model_validate(data)


def test_unverified_confidential_and_ineligible_evidence_fail_closed() -> None:
    unverified = _canonical_data()
    unverified["manifest"]["records"][0]["verification_status"] = "unverified"
    with pytest.raises(ValidationError):
        ProfileBundle.model_validate(unverified)

    confidential = _canonical_data()
    record = confidential["manifest"]["records"][0]
    record["confidentiality_and_attribution"]["public_reference_allowed"] = False
    with pytest.raises(ValidationError):
        PortfolioManifest.model_validate(confidential["manifest"])

    ineligible = _canonical_data()
    ineligible["manifest"]["records"][0]["proposal_eligible"] = False
    with pytest.raises(ValidationError, match="ineligible evidence"):
        ProfileBundle.model_validate(ineligible)


def test_duplicate_yaml_keys_and_invalid_values_raise_only_safe_exception(
    tmp_path: Path,
) -> None:
    duplicate = tmp_path / "profile.yaml"
    duplicate.write_text(
        "schema_version: '1.0'\nschema_version: 'private-value'\n",
        encoding="utf-8",
    )
    with pytest.raises(ProfileConfigurationError) as captured:
        ProfileBundleService.from_yaml(profile_path=duplicate)
    assert str(captured.value) == "profile configuration validation failed"
    assert "private-value" not in str(captured.value)
    assert str(tmp_path) not in str(captured.value)

    invalid = tmp_path / "invalid.yaml"
    invalid.write_text("private_client_secret: do-not-disclose\n", encoding="utf-8")
    with pytest.raises(ProfileConfigurationError) as invalid_captured:
        ProfileBundleService.from_yaml(profile_path=invalid)
    assert str(invalid_captured.value) == "profile configuration validation failed"
    assert "do-not-disclose" not in str(invalid_captured.value)


def test_models_are_frozen() -> None:
    profile = ProfileBundleService.from_yaml().bundle.profile
    with pytest.raises(ValidationError):
        profile.identity.display_name = "Changed"  # type: ignore[misc]


def test_kpis_have_executable_zero_denominator_and_target_contracts() -> None:
    metrics = ProfileBundleService.from_yaml().bundle.scoring.metrics
    required_metrics = {
        "relevant_jobs_surfaced_per_day",
        "surfaced_review_acceptance_rate",
        "review_relevance_rate",
        "light_edit_draft_rate",
        "unsupported_proposal_claim_count",
        "median_discovery_to_review_minutes",
        "applications_submitted_count",
        "replies_count",
        "interviews_count",
        "offers_count",
        "wins_count",
        "response_rate",
        "win_rate",
        "llm_cost_per_reviewed_job",
        "llm_cost_per_reply",
        "false_positive_rate",
        "proposal_factuality_trust_score",
        "unauthorized_external_action_count",
    }
    assert metrics
    assert {metric.metric_id for metric in metrics} == required_metrics
    assert all(metric.formula for metric in metrics)
    assert all(metric.numerator and metric.denominator for metric in metrics)
    assert all(metric.data_sources for metric in metrics)
    assert all(metric.initial_target.unit for metric in metrics)
    assert {metric.calculation.value for metric in metrics} == {
        "numerator_count",
        "ratio",
        "percentage",
        "median",
    }
    assert {
        metric.metric_id: metric.zero_denominator_behavior.value for metric in metrics
    }["review_relevance_rate"] == "not_available"
    assert {
        metric.metric_id: metric.initial_target.value for metric in metrics
    }["unsupported_proposal_claim_count"] == 0.0


def test_kpis_execute_nonzero_count_ratio_percentage_and_median_calculations() -> None:
    metrics = {
        metric.metric_id: metric
        for metric in ProfileBundleService.from_yaml().bundle.scoring.metrics
    }

    assert metrics["unsupported_proposal_claim_count"].evaluate(3.0, 10.0) == 3.0
    assert metrics["relevant_jobs_surfaced_per_day"].evaluate(12.0, 3.0) == 4.0
    assert metrics["review_relevance_rate"].evaluate(4.0, 5.0) == 80.0
    assert metrics["median_discovery_to_review_minutes"].evaluate(
        (1.0, 5.0, 2.0, 3.0), 4.0
    ) == 2.5


def test_kpis_honor_both_zero_denominator_behaviors() -> None:
    metrics = {
        metric.metric_id: metric
        for metric in ProfileBundleService.from_yaml().bundle.scoring.metrics
    }

    assert metrics["unsupported_proposal_claim_count"].evaluate(8.0, 0.0) == 0.0
    assert metrics["response_rate"].evaluate(0.0, 0.0) is None
    assert metrics["median_discovery_to_review_minutes"].evaluate((), 0.0) is None


@pytest.mark.parametrize(
    ("metric_id", "numerator", "denominator", "error"),
    (
        ("response_rate", float("nan"), 1.0, ValueError),
        ("response_rate", 1.0, float("inf"), ValueError),
        ("response_rate", -1.0, 1.0, ValueError),
        ("response_rate", 1.0, -1.0, ValueError),
        ("response_rate", 2.0, 1.0, ValueError),
        ("response_rate", (1.0,), 1.0, TypeError),
        ("median_discovery_to_review_minutes", 1.0, 1.0, TypeError),
        (
            "median_discovery_to_review_minutes",
            (1.0, float("inf")),
            2.0,
            ValueError,
        ),
        ("median_discovery_to_review_minutes", (1.0,), 2.0, ValueError),
    ),
)
def test_kpi_evaluation_rejects_invalid_or_inconsistent_inputs(
    metric_id: str,
    numerator: float | tuple[float, ...],
    denominator: float,
    error: type[Exception],
) -> None:
    metrics = {
        metric.metric_id: metric
        for metric in ProfileBundleService.from_yaml().bundle.scoring.metrics
    }

    with pytest.raises(error):
        metrics[metric_id].evaluate(numerator, denominator)


def test_private_inputs_are_ignored_and_only_scrubbed_metadata_is_tracked() -> None:
    root = Path(__file__).resolve().parents[1]
    git = ["git", "-c", f"safe.directory={root}"]
    ignored = (
        "data/private/private-profile.yaml",
        "data/private/proposal_history.json",
        "data/private/proposal_style_anchors/client-secret.md",
        "data/private/source-files/herbacorium.psd",
        "data/private/source-files/herbacorium.max",
    )
    for path in ignored:
        result = subprocess.run(
            [*git, "check-ignore", "--no-index", "--quiet", path],
            check=False,
            cwd=root,
        )
        assert result.returncode == 0, path

    tracked = subprocess.run(
        [*git, "ls-files", "data/private"],
        check=True,
        capture_output=True,
        cwd=root,
        text=True,
    ).stdout.splitlines()
    assert set(tracked) == {
        "data/private/README.md",
        "data/private/portfolio_manifest.yaml",
        "data/private/proposal_style_anchors/README.md",
    }
