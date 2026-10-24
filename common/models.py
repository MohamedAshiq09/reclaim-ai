from __future__ import annotations

from typing import Optional
from uagents import Model


class CaseFacts(Model):
    case_id: str
    category: str  # ecommerce | airline | bank | telecom | insurance | other
    company: str
    order_ref: Optional[str] = None
    amount_inr: Optional[float] = None
    order_date: Optional[str] = None
    issue_summary: str
    company_response: Optional[str] = None
    desired_outcome: str = "Full refund and formal grievance redressal"
    user_name: str = "Consumer"
    user_email: str = ""


class ResearchRequest(Model):
    facts: CaseFacts


class Citation(Model):
    title: str
    url: str
    section: Optional[str] = None
    note: str


class ResearchResult(Model):
    case_id: str
    rights_summary: str
    company_deadline_days: Optional[int] = 30
    grievance_email: Optional[str] = None
    grievance_source_url: Optional[str] = None
    next_tier_name: str = "National Consumer Helpline (NCH) / Consumer Court"
    next_tier_how: str = "File complaint at consumerhelpline.gov.in or e-Daakhil"
    citations: list[Citation] = []
    ok: bool = True
    error: Optional[str] = None


class DraftRequest(Model):
    facts: CaseFacts
    research: ResearchResult
    tier: int = 1  # 1 = Company Grievance Officer, 2 = Regulator / Ombudsman Escalation
    feedback: Optional[str] = None


class DraftResult(Model):
    case_id: str
    subject: str
    body: str
    tier: int = 1
    ok: bool = True
    error: Optional[str] = None


class DispatchRequest(Model):
    case_id: str
    to_email: str
    cc_email: str
    subject: str
    body: str
    request_id: Optional[str] = None


class DispatchResult(Model):
    case_id: str
    ok: bool = True
    message_id: Optional[str] = None
    fallback_text: Optional[str] = None
    error: Optional[str] = None


class WatcherRegisterCase(Model):
    case_id: str
    user_addr: str
    company: str
    deadline_seconds: int = 120  # Fast demo default


class WatcherEscalateTrigger(Model):
    case_id: str
    user_addr: str
    tier: int = 2
    reason: str
