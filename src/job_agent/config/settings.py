import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    env:str=os.getenv("JOB_AGENT_ENV","local")
    bind_host:str=os.getenv("JOB_AGENT_BIND_HOST","127.0.0.1")
    api_port:int=int(os.getenv("JOB_AGENT_API_PORT","8000"))
    database_url:str=os.getenv("JOB_AGENT_DATABASE_URL","sqlite:///job_agent.db")
    redis_url:str=os.getenv("JOB_AGENT_REDIS_URL","redis://localhost:6379/0")
    llm_enabled:bool=os.getenv("JOB_AGENT_LLM_ENABLED","false").lower()=="true"
    api_write_enabled:bool=os.getenv("JOB_AGENT_API_WRITE_ENABLED","false").lower()=="true"
    outreach_sending_enabled:bool=os.getenv("JOB_AGENT_OUTREACH_SENDING_ENABLED","false").lower()=="true"
    daily_cost_limit_usd:float=float(os.getenv("JOB_AGENT_DAILY_COST_LIMIT_USD","1.0"))
