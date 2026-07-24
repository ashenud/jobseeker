from __future__ import annotations

from enum import StrEnum
import math
from statistics import median
from typing import Annotated, Self
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictFloat,
    StrictInt,
    StrictStr,
    field_validator,
    model_validator,
)


Identifier = Annotated[StrictStr, Field(pattern=r"^[a-z][a-z0-9_]*$", min_length=1)]
ServiceIdentifier = Annotated[
    StrictStr, Field(pattern=r"^[a-z0-9][a-z0-9_]*$", min_length=1)
]
NonEmptyText = Annotated[StrictStr, Field(min_length=1)]
HttpUrl = Annotated[StrictStr, Field(min_length=1)]


class StrictProfileModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, populate_by_name=False)


def _duplicates(values: tuple[str, ...]) -> list[str]:
    return sorted(value for value in set(values) if values.count(value) > 1)


def _validate_http_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("URL must be absolute HTTP(S)")
    if parsed.username or parsed.password:
        raise ValueError("URL must not contain credentials")
    return value


class LanguageProficiency(StrEnum):
    native = "native"
    fluent = "fluent"
    professional = "professional"
    conversational = "conversational"


class EvidenceClassification(StrEnum):
    completed_client_work = "completed_client_work"
    personal_work = "personal_work"
    concept = "concept"
    speculative = "speculative"
    proposal_only = "proposal_only"


class VerificationStatus(StrEnum):
    owner_verified = "owner_verified"
    publicly_verified = "publicly_verified"
    owner_and_publicly_verified = "owner_and_publicly_verified"
    unverified = "unverified"


class ClaimLevel(StrEnum):
    completed_client_work = "completed_client_work"
    capability = "capability"


class UnknownBudgetAction(StrEnum):
    review = "review"
    reject = "reject"


class UnpaidCustomTestAction(StrEnum):
    reject = "reject"


class Cadence(StrEnum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    per_proposal = "per_proposal"


class ZeroDenominatorBehavior(StrEnum):
    not_available = "not_available"
    zero = "zero"


class KpiCalculation(StrEnum):
    numerator_count = "numerator_count"
    ratio = "ratio"
    percentage = "percentage"
    median = "median"


class TargetOperator(StrEnum):
    at_least = "at_least"
    at_most = "at_most"
    equals = "equals"


class Language(StrictProfileModel):
    language: NonEmptyText
    proficiency: LanguageProficiency


class Identity(StrictProfileModel):
    display_name: NonEmptyText
    primary_title: NonEmptyText
    timezone: NonEmptyText
    portfolio_url: HttpUrl
    languages: tuple[Language, ...] = Field(min_length=1)

    @field_validator("timezone")
    @classmethod
    def validate_iana_timezone(cls, value: str) -> str:
        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError("timezone must be an IANA timezone name") from exc
        return value

    @field_validator("portfolio_url")
    @classmethod
    def validate_portfolio_url(cls, value: str) -> str:
        return _validate_http_url(value)

    @model_validator(mode="after")
    def validate_unique_languages(self) -> Self:
        duplicates = _duplicates(tuple(item.language.casefold() for item in self.languages))
        if duplicates:
            raise ValueError("language names must be unique")
        return self


class Service(StrictProfileModel):
    service_id: ServiceIdentifier
    display_name: NonEmptyText
    priority: StrictInt = Field(ge=1, le=10)
    minimum_project_budget_usd: StrictInt = Field(ge=1)


class WorkingHoursOverlap(StrictProfileModel):
    minimum_hours_per_working_day: StrictInt = Field(ge=0, le=24)
    preferred_hours_per_working_day: StrictInt = Field(ge=0, le=24)
    maximum_hours_outside_sri_lankan_working_day: StrictInt = Field(ge=0, le=24)
    flexible_regions: tuple[NonEmptyText, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_hours(self) -> Self:
        if self.preferred_hours_per_working_day < self.minimum_hours_per_working_day:
            raise ValueError("preferred overlap must not be below minimum overlap")
        if (
            self.minimum_hours_per_working_day
            > self.maximum_hours_outside_sri_lankan_working_day
        ):
            raise ValueError("minimum overlap exceeds maximum outside-hours availability")
        return self


class GeographyRules(StrictProfileModel):
    strict_geographic_exclusions: tuple[NonEmptyText, ...]
    excluded_role_requirements: tuple[NonEmptyText, ...] = Field(min_length=1)


class UnpaidTestPolicy(StrictProfileModel):
    custom_design_test: UnpaidCustomTestAction
    portfolio_review_allowed: StrictBool
    interview_allowed: StrictBool
    maximum_unpaid_skill_assessment_minutes: StrictInt = Field(ge=0, le=30)
    substantial_or_client_ready_work_must_be_paid: StrictBool
    editable_source_files_must_be_paid: StrictBool


class WorkloadCaps(StrictProfileModel):
    maximum_reviews_per_day: StrictInt = Field(ge=1)
    targeted_applications_per_day: StrictInt = Field(ge=1)
    maximum_applications_per_day: StrictInt = Field(ge=1)

    @model_validator(mode="after")
    def validate_caps(self) -> Self:
        if self.targeted_applications_per_day > self.maximum_applications_per_day:
            raise ValueError("application target exceeds maximum")
        if self.maximum_applications_per_day > self.maximum_reviews_per_day:
            raise ValueError("application maximum exceeds review maximum")
        return self


class PreferredDuration(StrictProfileModel):
    preferred_engagements: tuple[NonEmptyText, ...] = Field(min_length=1)
    minimum_fixed_project_days: StrictInt = Field(ge=1)
    require_clear_scope_budget_milestones_and_payment_terms: StrictBool


class Constraints(StrictProfileModel):
    currency: Annotated[StrictStr, Field(pattern=r"^[A-Z]{3}$")]
    minimum_hourly_rate_usd: StrictInt = Field(ge=1)
    target_hourly_rate_usd: StrictInt = Field(ge=1)
    global_minimum_project_budget_usd: StrictInt = Field(ge=1)
    working_hours_overlap: WorkingHoursOverlap
    geography: GeographyRules
    unpaid_tests: UnpaidTestPolicy
    workload: WorkloadCaps
    preferred_duration: PreferredDuration
    excluded_industries: tuple[NonEmptyText, ...]
    excluded_deliverables: tuple[NonEmptyText, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_rates(self) -> Self:
        if self.target_hourly_rate_usd < self.minimum_hourly_rate_usd:
            raise ValueError("target hourly rate must not be below minimum")
        return self


class ProposalStyle(StrictProfileModel):
    minimum_words: StrictInt = Field(ge=1)
    maximum_words: StrictInt = Field(ge=1)
    tone: tuple[NonEmptyText, ...] = Field(min_length=1)
    avoid_phrases: tuple[NonEmptyText, ...] = Field(min_length=1)
    maximum_capabilities_to_mention: StrictInt = Field(ge=1, le=2)
    ask_useful_qualification_question_when_helpful: StrictBool
    include_portfolio_link_unless_platform_prohibits: StrictBool

    @model_validator(mode="after")
    def validate_word_range(self) -> Self:
        if self.maximum_words < self.minimum_words:
            raise ValueError("proposal maximum words must not be below minimum")
        return self


class ProposalClaim(StrictProfileModel):
    claim_id: Identifier
    text: NonEmptyText
    claim_level: ClaimLevel
    evidence_ids: tuple[Identifier, ...] = Field(min_length=1)
    allowed_in_proposals: StrictBool

    @model_validator(mode="after")
    def validate_evidence_ids(self) -> Self:
        if _duplicates(self.evidence_ids):
            raise ValueError("claim evidence IDs must be unique")
        return self


class ProfileConfig(StrictProfileModel):
    schema_version: Annotated[StrictStr, Field(pattern=r"^\d+\.\d+$")]
    identity: Identity
    services: tuple[Service, ...] = Field(min_length=1)
    constraints: Constraints
    proposal_style: ProposalStyle
    claims: tuple[ProposalClaim, ...]

    @model_validator(mode="after")
    def validate_taxonomy(self) -> Self:
        service_ids = tuple(service.service_id for service in self.services)
        claim_ids = tuple(claim.claim_id for claim in self.claims)
        if _duplicates(service_ids):
            raise ValueError("service IDs must be unique")
        if _duplicates(claim_ids):
            raise ValueError("claim IDs must be unique")
        floor = self.constraints.global_minimum_project_budget_usd
        if any(service.minimum_project_budget_usd < floor for service in self.services):
            raise ValueError("service budget must not be below global minimum")
        return self


class ScoreThresholds(StrictProfileModel):
    low_fit_below: StrictFloat = Field(ge=0, le=10)
    review_at_or_above: StrictFloat = Field(ge=0, le=10)
    priority_at_or_above: StrictFloat = Field(ge=0, le=10)

    @model_validator(mode="after")
    def validate_order(self) -> Self:
        if not self.low_fit_below <= self.review_at_or_above < self.priority_at_or_above:
            raise ValueError("scoring thresholds must be ordered")
        return self


class ScoringRules(StrictProfileModel):
    max_job_age_days: StrictInt = Field(ge=1)
    unknown_budget_action: UnknownBudgetAction
    currency: Annotated[StrictStr, Field(pattern=r"^[A-Z]{3}$")]
    minimum_fixed_budget_usd: StrictInt = Field(ge=1)
    minimum_hourly_rate_usd: StrictInt = Field(ge=1)
    max_review_jobs_per_day: StrictInt = Field(ge=1)
    max_applications_per_day: StrictInt = Field(ge=1)

    @model_validator(mode="after")
    def validate_caps(self) -> Self:
        if self.max_applications_per_day > self.max_review_jobs_per_day:
            raise ValueError("scoring application cap exceeds review cap")
        return self


class ScoreDimension(StrictProfileModel):
    dimension_id: Identifier
    weight: StrictFloat = Field(gt=0, le=1)

    @field_validator("weight")
    @classmethod
    def validate_finite_weight(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("dimension weight must be finite")
        return value


class KpiTarget(StrictProfileModel):
    operator: TargetOperator
    value: StrictFloat = Field(ge=0)
    unit: NonEmptyText

    @field_validator("value")
    @classmethod
    def validate_finite_target(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("KPI target must be finite")
        return value


class KpiDefinition(StrictProfileModel):
    metric_id: Identifier
    display_name: NonEmptyText
    calculation: KpiCalculation
    formula: NonEmptyText
    numerator: NonEmptyText
    denominator: NonEmptyText
    zero_denominator_behavior: ZeroDenominatorBehavior
    data_sources: tuple[Identifier, ...] = Field(min_length=1)
    cadence: Cadence
    initial_target: KpiTarget

    @model_validator(mode="after")
    def validate_sources(self) -> Self:
        if _duplicates(self.data_sources):
            raise ValueError("KPI data sources must be unique")
        return self

    def evaluate(
        self,
        numerator_value: float | tuple[float, ...],
        denominator_value: float,
    ) -> float | None:
        denominator = self._finite_non_negative(
            denominator_value, label="denominator"
        )

        if self.calculation == KpiCalculation.median:
            if not isinstance(numerator_value, tuple):
                raise TypeError("median KPI numerator must be a tuple of observations")
            observations = tuple(
                self._finite_non_negative(value, label="observation")
                for value in numerator_value
            )
            if denominator != len(observations):
                raise ValueError(
                    "median KPI denominator must equal the observation count"
                )
            if denominator == 0:
                return self._zero_denominator_result()
            return float(median(observations))

        if isinstance(numerator_value, tuple):
            raise TypeError("non-median KPI numerator must be a scalar")
        numerator = self._finite_non_negative(numerator_value, label="numerator")
        if denominator == 0:
            return self._zero_denominator_result()
        if self.calculation == KpiCalculation.numerator_count:
            return numerator
        if self.calculation == KpiCalculation.ratio:
            return numerator / denominator
        if numerator > denominator:
            raise ValueError("percentage KPI numerator must not exceed denominator")
        return numerator / denominator * 100.0

    @staticmethod
    def _finite_non_negative(value: float, *, label: str) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"KPI {label} must be a number")
        result = float(value)
        if not math.isfinite(result):
            raise ValueError(f"KPI {label} must be finite")
        if result < 0:
            raise ValueError(f"KPI {label} must be non-negative")
        return result

    def _zero_denominator_result(self) -> float | None:
        if self.zero_denominator_behavior == ZeroDenominatorBehavior.zero:
            return 0.0
        return None


class PilotBehavior(StrictProfileModel):
    archive_low_scores: StrictBool
    auto_discard: StrictBool


class ScoringConfig(StrictProfileModel):
    schema_version: Annotated[StrictStr, Field(pattern=r"^\d+\.\d+$")]
    thresholds: ScoreThresholds
    rules: ScoringRules
    dimensions: tuple[ScoreDimension, ...] = Field(min_length=1)
    metrics: tuple[KpiDefinition, ...] = Field(min_length=1)
    pilot: PilotBehavior

    @model_validator(mode="after")
    def validate_dimensions_and_metrics(self) -> Self:
        dimension_ids = tuple(item.dimension_id for item in self.dimensions)
        metric_ids = tuple(item.metric_id for item in self.metrics)
        if _duplicates(dimension_ids):
            raise ValueError("scoring dimension IDs must be unique")
        if _duplicates(metric_ids):
            raise ValueError("KPI metric IDs must be unique")
        if not math.isclose(
            sum(item.weight for item in self.dimensions),
            1.0,
            rel_tol=0,
            abs_tol=1e-9,
        ):
            raise ValueError("scoring dimension weights must sum to 1")
        return self


class EvidenceSource(StrictProfileModel):
    source_type: Identifier
    public_source: NonEmptyText
    public_reference_url: HttpUrl
    owner_verified: StrictBool
    owner_verified_record_types: tuple[NonEmptyText, ...] = Field(min_length=1)

    @field_validator("public_reference_url")
    @classmethod
    def validate_public_reference_url(cls, value: str) -> str:
        return _validate_http_url(value)

    @model_validator(mode="after")
    def validate_record_types(self) -> Self:
        if _duplicates(self.owner_verified_record_types):
            raise ValueError("owner-verified record types must be unique")
        return self


class EvidenceRole(StrictProfileModel):
    title: NonEmptyText
    responsibilities: tuple[NonEmptyText, ...] = Field(min_length=1)


class ProposalReference(StrictProfileModel):
    allowed: StrictBool
    evidence_strength: Identifier
    suitable_for: tuple[NonEmptyText, ...] = Field(min_length=1)
    approved_short_reference: NonEmptyText
    approved_detailed_reference: NonEmptyText


class ConfidentialityAndAttribution(StrictProfileModel):
    confidentiality_level: Identifier
    public_reference_allowed: StrictBool
    restrictions: tuple[NonEmptyText, ...] = Field(min_length=1)


class EvidenceRecord(StrictProfileModel):
    evidence_id: Identifier
    project_title: NonEmptyText
    evidence_source: EvidenceSource
    verification_status: VerificationStatus
    classification: EvidenceClassification
    role: EvidenceRole
    deliverables_and_services: tuple[NonEmptyText, ...] = Field(min_length=1)
    tools_and_workflow: tuple[NonEmptyText, ...] = Field(min_length=1)
    safe_claims: tuple[NonEmptyText, ...] = Field(min_length=1)
    claims_requiring_additional_evidence: tuple[NonEmptyText, ...] = Field(min_length=1)
    proposal_reference: ProposalReference
    confidentiality_and_attribution: ConfidentialityAndAttribution
    proposal_eligible: StrictBool
    completed_work_claim_allowed: StrictBool
    public_visuals_allowed: StrictBool
    source_files_allowed: StrictBool
    performance_claims_allowed: StrictBool
    supported_service_ids: tuple[ServiceIdentifier, ...] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_record_consistency(self) -> Self:
        if _duplicates(self.supported_service_ids):
            raise ValueError("supported service IDs must be unique")
        if _duplicates(self.safe_claims):
            raise ValueError("safe claims must be unique")
        verified = self.verification_status != VerificationStatus.unverified
        if self.proposal_eligible and not verified:
            raise ValueError("unverified evidence cannot be proposal eligible")
        if self.proposal_eligible and not self.proposal_reference.allowed:
            raise ValueError("proposal-eligible evidence must allow proposal references")
        if (
            self.completed_work_claim_allowed
            and self.classification != EvidenceClassification.completed_client_work
        ):
            raise ValueError("non-client work cannot allow completed-work claims")
        if self.completed_work_claim_allowed and not verified:
            raise ValueError("unverified evidence cannot allow completed-work claims")
        if (
            self.proposal_reference.allowed
            and not self.confidentiality_and_attribution.public_reference_allowed
        ):
            raise ValueError("proposal reference conflicts with confidentiality")
        return self


class PortfolioManifest(StrictProfileModel):
    schema_version: Annotated[StrictStr, Field(pattern=r"^\d+\.\d+$")]
    portfolio_url: HttpUrl
    records: tuple[EvidenceRecord, ...] = Field(min_length=1)

    @field_validator("portfolio_url")
    @classmethod
    def validate_portfolio_url(cls, value: str) -> str:
        return _validate_http_url(value)

    @model_validator(mode="after")
    def validate_unique_records(self) -> Self:
        evidence_ids = tuple(item.evidence_id for item in self.records)
        if _duplicates(evidence_ids):
            raise ValueError("evidence IDs must be unique")
        return self


class ProfileBundle(StrictProfileModel):
    profile: ProfileConfig
    scoring: ScoringConfig
    manifest: PortfolioManifest

    @model_validator(mode="after")
    def validate_cross_file_contract(self) -> Self:
        if self.profile.identity.portfolio_url != self.manifest.portfolio_url:
            raise ValueError("profile and manifest portfolio URLs differ")

        constraints = self.profile.constraints
        rules = self.scoring.rules
        expected_rules = (
            constraints.currency,
            constraints.global_minimum_project_budget_usd,
            constraints.minimum_hourly_rate_usd,
            constraints.workload.maximum_reviews_per_day,
            constraints.workload.maximum_applications_per_day,
        )
        actual_rules = (
            rules.currency,
            rules.minimum_fixed_budget_usd,
            rules.minimum_hourly_rate_usd,
            rules.max_review_jobs_per_day,
            rules.max_applications_per_day,
        )
        if actual_rules != expected_rules:
            raise ValueError("profile constraints and scoring rules contradict")

        service_ids = {item.service_id for item in self.profile.services}
        evidence_by_id = {item.evidence_id: item for item in self.manifest.records}
        for evidence_record in self.manifest.records:
            if not set(evidence_record.supported_service_ids) <= service_ids:
                raise ValueError("evidence references an unknown service ID")

        for claim in self.profile.claims:
            if not claim.allowed_in_proposals:
                continue
            for evidence_id in claim.evidence_ids:
                claim_evidence: EvidenceRecord | None = evidence_by_id.get(evidence_id)
                if claim_evidence is None:
                    raise ValueError("proposal claim has dangling evidence")
                if not claim_evidence.proposal_eligible:
                    raise ValueError("proposal claim uses ineligible evidence")
                if claim.text not in claim_evidence.safe_claims:
                    raise ValueError("proposal claim is not approved by evidence")
                if (
                    claim.claim_level == ClaimLevel.completed_client_work
                    and not claim_evidence.completed_work_claim_allowed
                ):
                    raise ValueError("completed-work claim uses restricted evidence")
        return self
