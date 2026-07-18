from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from .exceptions import PolicyDeniedError
from .models import (
    NETWORK_ACTIONS,
    WRITE_ACTIONS,
    PolicyAction,
    PolicyDecision,
    PolicyMode,
    PolicyRegistry,
)


@dataclass(frozen=True)
class RuntimeFlags: api_write_enabled:bool=False; browser_fill_enabled:bool=False; outreach_sending_enabled:bool=False; confirmation_ttl_seconds:int=300
@dataclass
class ConfirmationRecord: token_hash:str; platform_id:str; action:PolicyAction; destination:str; checksum:str; expires_at:datetime; used:bool=False
class ConfirmationTokenService:
    def __init__(self)->None: self._records:dict[str,ConfirmationRecord]={}
    def issue(self, platform_id:str, action:PolicyAction, destination:str, checksum:str, ttl_seconds:int=300)->str:
        token=secrets.token_urlsafe(24); digest=hashlib.sha256(token.encode()).hexdigest(); self._records[digest]=ConfirmationRecord(digest,platform_id,action,destination,checksum,datetime.now(UTC)+timedelta(seconds=ttl_seconds)); return token
    def consume(self, token:str, platform_id:str, action:PolicyAction, destination:str, checksum:str)->bool:
        rec=self._records.get(hashlib.sha256(token.encode()).hexdigest())
        if not rec or rec.used or rec.expires_at<datetime.now(UTC): return False
        if (rec.platform_id,rec.action,rec.destination,rec.checksum)!=(platform_id,action,destination,checksum): return False
        rec.used=True; return True
class PolicyService:
    def __init__(self, registry:PolicyRegistry, today:date|None=None, flags:RuntimeFlags|None=None, tokens:ConfirmationTokenService|None=None):
        self.registry=registry; self.today=today or date.today(); self.flags=flags or RuntimeFlags(); self.tokens=tokens or ConfirmationTokenService(); self._by_id={p.platform_id:p for p in registry.platforms}
    @classmethod
    def from_yaml(cls,path:Path|str="config/platform_policy.yaml", **kwargs:object)->PolicyService:
        return cls(PolicyRegistry.from_dict(json.loads(Path(path).read_text())), **kwargs)
    def decide(self, platform_id:str, action:PolicyAction|str, network:bool=False, confirmation_token:str|None=None, destination:str="", checksum:str="") -> PolicyDecision:
        act=PolicyAction(action); platform=self._by_id.get(platform_id)
        if not platform: return PolicyDecision(platform_id,act,None,False,"Unknown platform denied",self.registry.version)
        mode=platform.actions.get(act)
        if mode is None: return PolicyDecision(platform_id,act,None,False,"Unknown action denied",self.registry.version,platform.review_due_at)
        if platform.review_due_at < self.today and (network or act in NETWORK_ACTIONS or mode in {PolicyMode.public_feed,PolicyMode.official_api_read,PolicyMode.official_api_write_with_confirmation}): return PolicyDecision(platform_id,act,mode,False,"Policy review expired",self.registry.version,platform.review_due_at)
        allowed=mode==PolicyMode.internal_test_fixture or (mode==PolicyMode.manual_only and not network and act not in WRITE_ACTIONS) or (mode in {PolicyMode.public_feed,PolicyMode.official_api_read} and act not in WRITE_ACTIONS)
        if mode==PolicyMode.official_api_write_with_confirmation: allowed=self.flags.api_write_enabled and bool(confirmation_token) and self.tokens.consume(confirmation_token,platform_id,act,destination,checksum)
        return PolicyDecision(platform_id,act,mode,allowed,"Allowed by current policy" if allowed else f"Mode {mode or 'missing'} does not permit requested operation",self.registry.version,platform.review_due_at)
    def require(self,*args:object,**kwargs:object)->PolicyDecision:
        d=self.decide(*args,**kwargs)
        if not d.allowed: raise PolicyDeniedError(d.reason)
        return d
