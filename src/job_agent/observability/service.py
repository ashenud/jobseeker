from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from job_agent.security.service import redact


@dataclass
class MetricRegistry:
    counters:dict[str,int]=field(default_factory=dict)
    def inc(self,name:str,amount:int=1)->None: self.counters[name]=self.counters.get(name,0)+amount
    def render(self)->str: return "\n".join(f"{k} {v}" for k,v in sorted(self.counters.items()))
def log_event(service:str,outcome:str,**fields:object)->dict[str,object]:
    return {"timestamp":datetime.now(UTC).isoformat(),"service":service,"outcome":outcome,**{k:redact(str(v)) for k,v in fields.items()}}
