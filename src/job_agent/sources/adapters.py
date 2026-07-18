from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from job_agent.policy.models import PolicyAction
from job_agent.policy.service import PolicyService


@dataclass(frozen=True)
class RawItem: source_id:str; platform_id:str; external_id:str; url:str; title:str; body:str
class SourceAdapter(Protocol):
    platform_id:str
    def fetch(self, cursor:str|None=None)->list[RawItem]: ...
class ManualAdapter:
    platform_id="manual"
    def capture(self, url:str, title:str, body:str)->RawItem: return RawItem("manual","manual",str(abs(hash((url,title,body)))),url,title,body)
class FixtureFeedAdapter:
    def __init__(self, platform_id:str, policy:PolicyService, items:list[dict[str,str]]): self.platform_id=platform_id; self.policy=policy; self.items=items; self.network_called=False
    def fetch(self,cursor:str|None=None)->list[RawItem]:
        self.policy.require(self.platform_id,PolicyAction.discover,network=True)
        self.network_called=True
        return [RawItem(self.platform_id,self.platform_id,i["id"],i["url"],i["title"],i["body"]) for i in self.items]
class SourceRegistry:
    def __init__(self)->None: self._adapters:dict[str,SourceAdapter]={}
    def register(self, name:str, adapter:SourceAdapter)->None: self._adapters[name]=adapter
    def list(self)->list[str]: return sorted(self._adapters)
