from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4


@dataclass(frozen=True)
class RawJob:
    platform_id:str; external_id:str; payload:str; id:str=field(default_factory=lambda: str(uuid4())); created_at:datetime=field(default_factory=lambda: datetime.now(UTC))
@dataclass(frozen=True)
class ProposalRevision:
    proposal_id:str; body:str; id:str=field(default_factory=lambda: str(uuid4())); created_at:datetime=field(default_factory=lambda: datetime.now(UTC))
