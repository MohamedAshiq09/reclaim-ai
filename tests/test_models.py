from common.models import (
    CaseFacts,
    Citation,
    DispatchRequest,
    DispatchResult,
    DraftRequest,
    DraftResult,
    ResearchRequest,
    ResearchResult,
)


def test_case_facts_model():
    facts = CaseFacts(
        case_id="REC-TEST01",
        category="ecommerce",
        company="Flipkart",
        order_ref="OD1234567890",
        amount_inr=24999.0,
        issue_summary="Delivered cracked smartphone display; refund denied.",
        user_name="Rajesh Kumar",
        user_email="rajesh@example.com",
    )
    assert facts.case_id == "REC-TEST01"
    assert facts.company == "Flipkart"
    assert facts.amount_inr == 24999.0


def test_research_models():
    citation = Citation(
        title="Consumer Protection (E-Commerce) Rules, 2020",
        url="https://consumeraffairs.nic.in",
        section="Rule 4(4) & Rule 4(5)",
        note="48h acknowledgment and 30d redressal",
    )
    res = ResearchResult(
        case_id="REC-TEST01",
        rights_summary="Mandatory statutory resolution required.",
        company_deadline_days=30,
        grievance_email="grievance.officer@flipkart.com",
        citations=[citation],
        ok=True,
    )
    assert res.case_id == "REC-TEST01"
    assert len(res.citations) == 1
    assert res.citations[0].section == "Rule 4(4) & Rule 4(5)"



def test_draft_models():
    facts = CaseFacts(
        case_id="REC-TEST01",
        category="ecommerce",
        company="Flipkart",
        issue_summary="Broken screen",
        user_name="Rajesh",
        user_email="rajesh@example.com",
    )
    research = ResearchResult(
        case_id="REC-TEST01",
        rights_summary="Summary",
        company_deadline_days=30,
        grievance_email="grievance@flipkart.com",
        ok=True,
    )
    req = DraftRequest(facts=facts, research=research, tier=1)
    res = DraftResult(
        case_id="REC-TEST01",
        subject="FORMAL NOTICE",
        body="Dear Grievance Officer...",
        ok=True,
    )
    assert req.facts.company == "Flipkart"
    assert res.subject == "FORMAL NOTICE"


def test_dispatch_models():
    req = DispatchRequest(
        case_id="REC-TEST01",
        to_email="grievance@flipkart.com",
        cc_email="rajesh@example.com",
        subject="Subject",
        body="Body",
    )
    res = DispatchResult(case_id="REC-TEST01", ok=True, message_id="msg_123")
    assert req.to_email == "grievance@flipkart.com"
    assert res.ok is True
    assert res.message_id == "msg_123"
