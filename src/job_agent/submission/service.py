from __future__ import annotations

import hashlib
from dataclasses import dataclass

from job_agent.policy.models import PolicyAction
from job_agent.policy.service import PolicyService


@dataclass(frozen=True)
class SubmissionPackage: platform_id:str; destination_url:str; proposal_body:str; checksum:str; status:str="prepared"
def build_package(platform_id:str, destination_url:str, proposal_body:str)->SubmissionPackage:
    return SubmissionPackage(platform_id,destination_url,proposal_body,hashlib.sha256(proposal_body.encode()).hexdigest())
def mark_manual_submitted(package:SubmissionPackage, reference:str)->dict[str,str]:
    if not reference: raise ValueError("reference required")
    return {"status":"submitted","reference":reference,"mode":"manual"}
class FakeWriteConnector:
    def __init__(self, policy:PolicyService): self.policy=policy; self.sent: list[str]=[]
    def submit(self, package:SubmissionPackage, confirmation_token:str|None)->str:
        self.policy.require(package.platform_id,PolicyAction.submit,network=True,confirmation_token=confirmation_token,destination=package.destination_url,checksum=package.checksum)
        self.sent.append(package.checksum); return "dry-run-receipt"
