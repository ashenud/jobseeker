from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from job_agent.sources.adapters import RawItem


@dataclass(frozen=True)
class CanonicalJob: fingerprint:str; platform_id:str; url:str; title:str; description:str; services:list[str]; budget:str|None; warnings:list[str]
TRACKING={"utm_source","utm_medium","utm_campaign","utm_term","utm_content","fbclid","gclid"}
def canonical_url(url:str)->str:
    parts=urlsplit(url); q=urlencode([(k,v) for k,v in parse_qsl(parts.query) if k not in TRACKING])
    return urlunsplit((parts.scheme.lower(),parts.netloc.lower(),parts.path.rstrip("/"),q,""))
def normalize(raw:RawItem)->CanonicalJob:
    text=re.sub(r"<[^>]+>"," ",raw.body); text=re.sub(r"\s+"," ",text).strip()
    low=f"{raw.title} {text}".lower(); services=[]
    for key,terms in {"packaging_label":["packaging","label","dieline"],"amazon_content":["amazon","a+"],"brand_identity":["logo","brand identity"],"3d_visualization":["3d","render","visualization"],"architectural_visualization":["architectural","interior","exterior"]}.items():
        if any(t in low for t in terms): services.append(key)
    budget_match=re.search(r"(\$|usd)\s?([0-9][0-9,]*(?:\.[0-9]+)?)",low)
    url=canonical_url(raw.url); fp=hashlib.sha256(f"{raw.platform_id}|{url}|{raw.title.strip().lower()}".encode()).hexdigest()
    return CanonicalJob(fp,raw.platform_id,url,raw.title.strip(),text,services,budget_match.group(0) if budget_match else None,[] if budget_match else ["budget_unknown"])
def rule_decision(job:CanonicalJob)->tuple[str,list[str]]:
    reasons=[]
    if not job.services: reasons.append("no_matching_design_service")
    if any(x in job.description.lower() for x in ["captcha","bulk apply","free sample"]): reasons.append("red_flag")
    return ("reject" if reasons else "keep", reasons)
