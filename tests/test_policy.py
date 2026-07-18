from datetime import date

import pytest

from job_agent.policy.exceptions import PolicyDeniedError
from job_agent.policy.models import PolicyAction, PolicyRegistry
from job_agent.policy.service import ConfirmationTokenService, PolicyService, RuntimeFlags
from job_agent.submission.service import FakeWriteConnector, build_package


def svc(**kw): return PolicyService.from_yaml(today=date(2026,7,18), **kw)
def test_unknown_platform_and_action_denied():
    assert not svc().decide("missing", "discover").allowed
    assert not svc().decide("remote_ok", "submit", network=True).allowed
def test_manual_only_prevents_network_before_connector_call():
    with pytest.raises(PolicyDeniedError): svc().require("behance", PolicyAction.discover, network=True)
def test_expired_review_denies_network():
    assert not PolicyService.from_yaml(today=date(2027,1,1)).decide("remote_ok","discover",network=True).allowed
def test_submission_needs_feature_flag_and_confirmation():
    tokens=ConfirmationTokenService(); flags=RuntimeFlags(api_write_enabled=True); service=svc(flags=flags,tokens=tokens)
    data=service.registry.to_dict(); data["platforms"][0]["owner_approved"]=True; data["platforms"][0]["actions"]["submit"]="official_api_write_with_confirmation"
    service=PolicyService(PolicyRegistry.from_dict(data),today=date(2026,7,18),flags=flags,tokens=tokens)
    package=build_package("behance","https://example.test/job","hello")
    with pytest.raises(PolicyDeniedError): FakeWriteConnector(service).submit(package,None)
    token=tokens.issue("behance",PolicyAction.submit,package.destination_url,package.checksum)
    assert FakeWriteConnector(service).submit(package,token)=="dry-run-receipt"
    with pytest.raises(PolicyDeniedError): FakeWriteConnector(service).submit(package,token)
def test_configuration_validation_rejects_contradictory_settings():
    data=svc().registry.to_dict(); data["platforms"][0]["actions"]["submit"]="official_api_write_with_confirmation"
    with pytest.raises(ValueError): PolicyRegistry.from_dict(data)
