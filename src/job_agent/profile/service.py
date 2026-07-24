from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError
import yaml

from .exceptions import ProfileConfigurationError
from .models import ProfileBundle, ProfileConfig, PortfolioManifest, ScoringConfig


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_unique_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[object, object]:
    loader.flatten_mapping(node)
    mapping: dict[object, object] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ProfileConfigurationError from exc
        if duplicate:
            raise ProfileConfigurationError
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


def _load_yaml(path: Path | str) -> object:
    try:
        return yaml.load(Path(path).read_text(encoding="utf-8"), Loader=_UniqueKeyLoader)
    except ProfileConfigurationError:
        raise
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise ProfileConfigurationError from exc


class ProfileBundleService:
    def __init__(self, bundle: ProfileBundle) -> None:
        self.bundle = bundle

    @classmethod
    def from_yaml(
        cls,
        profile_path: Path | str = "config/profile.yaml",
        scoring_path: Path | str = "config/scoring.yaml",
        manifest_path: Path | str = "data/private/portfolio_manifest.yaml",
    ) -> ProfileBundleService:
        try:
            profile = ProfileConfig.model_validate(_load_yaml(profile_path))
            scoring = ScoringConfig.model_validate(_load_yaml(scoring_path))
            manifest = PortfolioManifest.model_validate(_load_yaml(manifest_path))
            bundle = ProfileBundle(profile=profile, scoring=scoring, manifest=manifest)
        except ProfileConfigurationError:
            raise
        except (ValidationError, TypeError, ValueError) as exc:
            raise ProfileConfigurationError from exc
        return cls(bundle)

    def validation_summary(self) -> dict[str, object]:
        proposal_claims = tuple(
            claim for claim in self.bundle.profile.claims if claim.allowed_in_proposals
        )
        return {
            "result": "PASS",
            "schema_versions": {
                "profile": self.bundle.profile.schema_version,
                "scoring": self.bundle.scoring.schema_version,
                "portfolio_manifest": self.bundle.manifest.schema_version,
            },
            "counts": {
                "services": len(self.bundle.profile.services),
                "evidence_records": len(self.bundle.manifest.records),
                "proposal_eligible_claims": len(proposal_claims),
                "metrics": len(self.bundle.scoring.metrics),
            },
            "dangling_evidence_ids": [],
            "ineligible_evidence_ids": [],
            "contradictions": [],
        }
