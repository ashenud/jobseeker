from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class PolicyMode(StrEnum):
    disabled="disabled"; manual_only="manual_only"; public_feed="public_feed"; official_api_read="official_api_read"; official_api_write_with_confirmation="official_api_write_with_confirmation"; internal_test_fixture="internal_test_fixture"
class PolicyAction(StrEnum):
    discover="discover"; read_detail="read_detail"; store="store"; notify="notify"; draft="draft"; open_link="open_link"; submit="submit"; message="message"; follow_up="follow_up"
NETWORK_ACTIONS={PolicyAction.discover,PolicyAction.read_detail}; WRITE_ACTIONS={PolicyAction.submit,PolicyAction.message,PolicyAction.follow_up}
@dataclass(frozen=True)
class PlatformLimits: requests_per_minute:int; retention_days:int
@dataclass(frozen=True)
class PlatformPolicy:
    platform_id:str; display_name:str; reviewed_at:date; review_due_at:date; terms_url:str; help_or_api_url:str|None; owner_approved:bool; actions:dict[PolicyAction,PolicyMode]; limits:PlatformLimits; notes:str=""
@dataclass(frozen=True)
class PolicyRegistry:
    version:str; platforms:list[PlatformPolicy]
    @classmethod
    def from_dict(cls, data:dict[str,object])->PolicyRegistry:
        plats=[]
        for raw in data["platforms"]:  # type: ignore[index]
            r=dict(raw)  # type: ignore[arg-type]
            actions={PolicyAction(k):PolicyMode(v) for k,v in dict(r["actions"]).items()}
            limits=PlatformLimits(**dict(r["limits"]))
            p=PlatformPolicy(platform_id=str(r["platform_id"]),display_name=str(r["display_name"]),reviewed_at=date.fromisoformat(str(r["reviewed_at"])),review_due_at=date.fromisoformat(str(r["review_due_at"])),terms_url=str(r["terms_url"]),help_or_api_url=None if r.get("help_or_api_url") is None else str(r.get("help_or_api_url")),owner_approved=bool(r["owner_approved"]),actions=actions,limits=limits,notes=str(r.get("notes","")))
            for action,mode in actions.items():
                if action in WRITE_ACTIONS and mode==PolicyMode.official_api_write_with_confirmation and not p.owner_approved: raise ValueError(f"{p.platform_id}:{action} write mode requires owner_approved")
                if mode in {PolicyMode.public_feed,PolicyMode.official_api_read} and limits.requests_per_minute<=0: raise ValueError(f"{p.platform_id}:{action} network mode needs positive rate limit")
            plats.append(p)
        return cls(version=str(data["version"]), platforms=plats)
    def to_dict(self)->dict[str,object]:
        return {"version":self.version,"platforms":[{"platform_id":p.platform_id,"display_name":p.display_name,"reviewed_at":p.reviewed_at.isoformat(),"review_due_at":p.review_due_at.isoformat(),"terms_url":p.terms_url,"help_or_api_url":p.help_or_api_url,"owner_approved":p.owner_approved,"actions":{k.value:v.value for k,v in p.actions.items()},"limits":{"requests_per_minute":p.limits.requests_per_minute,"retention_days":p.limits.retention_days},"notes":p.notes} for p in self.platforms]}
@dataclass(frozen=True)
class PolicyDecision:
    platform_id:str; action:PolicyAction; mode:PolicyMode|None; allowed:bool; reason:str; policy_version:str; review_due_at:date|None=None
    def to_json(self)->str:
        import json
        return json.dumps({"platform_id":self.platform_id,"action":self.action.value,"mode":None if self.mode is None else self.mode.value,"allowed":self.allowed,"reason":self.reason,"policy_version":self.policy_version,"review_due_at":None if self.review_due_at is None else self.review_due_at.isoformat()})
