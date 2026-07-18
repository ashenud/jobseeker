from dataclasses import dataclass, field


@dataclass(frozen=True)
class EvidenceChunk:
    chunk_id:str; title:str; text:str; services:list[str]; verification_state:str; claim_level:str; public_url:str|None=None; restrictions:list[str]=field(default_factory=list)
ELIGIBLE={"verified_public","verified_private"}
def retrieve(services:list[str], chunks:list[EvidenceChunk])->list[EvidenceChunk]: return [c for c in chunks if c.verification_state in ELIGIBLE and any(s in c.services for s in services) and c.claim_level!="proposal_only"]
