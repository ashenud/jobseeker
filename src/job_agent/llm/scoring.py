from dataclasses import dataclass, field

from job_agent.normalization.service import CanonicalJob


@dataclass(frozen=True)
class Dimension: score:int; reasons:list[str]=field(default_factory=list)
@dataclass(frozen=True)
class ScoreResult:
    overall_score:float; decision:str; confidence:float; dimensions:dict[str,Dimension]; red_flags:list[str]; missing_information:list[str]; suggested_angle:str; pricing_approach:str; prompt_version:str="score-v1"; schema_version:str="1.0"; provider:str="fake"; model:str="offline-rules"
def score_job(job:CanonicalJob)->ScoreResult:
    service=9 if job.services else 2; budget=7 if job.budget else 4; overall=(service+budget+7)/3
    return ScoreResult(round(overall,1),"priority" if overall>=7 else "skip",.8,{"service_match":Dimension(service,job.services or ["No service match"]),"budget_fit":Dimension(budget,[job.budget or "Budget missing"]),"scope_clarity":Dimension(7,[])},[],[] if job.budget else ["budget"],"Lead with relevant design/3D experience.","Confirm scope before quoting.")
class BudgetGuard:
    def __init__(self, daily_limit_usd:float): self.daily_limit_usd=daily_limit_usd; self.spent=0.0
    def reserve(self, amount:float)->None:
        if self.spent+amount>self.daily_limit_usd: raise RuntimeError("LLM budget exhausted")
        self.spent+=amount
