from dataclasses import dataclass, field

from job_agent.evidence.service import EvidenceChunk
from job_agent.normalization.service import CanonicalJob


@dataclass(frozen=True)
class EvidenceLink: claim_text:str; evidence_ids:list[str]
@dataclass(frozen=True)
class ProposalResult:
    body:str; opening:str; question:str; evidence_links:list[EvidenceLink]; warnings:list[str]=field(default_factory=list); platform_checks:dict[str,bool]=field(default_factory=dict); prompt_version:str="proposal-v1"; schema_version:str="1.0"
def generate_proposal(job:CanonicalJob, evidence:list[EvidenceChunk], allow_link:bool=True)->ProposalResult:
    safe_title=job.title.replace("ignore previous instructions","").strip(); warnings=[] if evidence else ["unsupported_claims_block_review"]
    claim=f"I can help with {', '.join(job.services) or 'the requested design work'} using verified portfolio evidence."
    body=f"Hi, your {safe_title} brief is a good fit. {claim} I would first confirm scope, deliverables, timeline, and source files. Could you share the final deliverable list and deadline?"
    if allow_link: body += " Portfolio: https://www.behance.net/47pixels"
    return ProposalResult(body,f"Hi, your {safe_title} brief is a good fit.","Could you share the final deliverable list and deadline?",[EvidenceLink(claim,[e.chunk_id for e in evidence])],warnings,{"length_ok":len(body)<1200,"external_link_allowed":allow_link,"contact_details_allowed":False})
