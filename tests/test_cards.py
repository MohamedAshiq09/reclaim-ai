import json
from common.cards import (
    build_carousel_card,
    build_detail_card,
    build_form_card,
    build_review_card,
    card_message,
    parse_selection,
)
from uagents_core.contrib.protocols.chat import MetadataContent, TextContent


def test_card_message_structure():
    payload = {"key": "value"}
    msg = card_message(
        narration="Test narration",
        card_kind="detail",
        payload=payload,
        is_terminal=False,
    )
    assert len(msg.content) == 2
    assert isinstance(msg.content[0], TextContent)
    assert isinstance(msg.content[1], MetadataContent)

    meta = msg.content[1].metadata
    assert meta["card_protocol_version"] == "1"
    assert meta["card_kind"] == "detail"
    assert meta["requires_card_interaction"] == "true"
    assert meta["is_terminal"] == "false"
    assert json.loads(meta["card_payload"]) == payload


def test_build_form_card():
    fields = [
        {"name": "company", "kind": "text", "label": "Company", "required": True},
        {"name": "amount", "kind": "number", "label": "Amount", "required": False},
    ]
    card = build_form_card(title="Test Form", fields=fields)
    assert card["title"] == "Test Form"
    assert len(card["fields"]) == 2
    assert card["submit_cta"]["selection"]["action"] == "submit_case_facts"


def test_build_review_card():
    rows = [{"label": "Order", "value": "12345"}]
    card = build_review_card(title="Review Notice", summary_rows=rows)
    assert card["title"] == "Review Notice"
    assert card["approve_cta"]["selection"]["action"] == "approve_dispatch"
    assert card["reject_cta"]["selection"]["action"] == "reject_or_edit"


def test_build_detail_card():
    rows = [{"label": "Deadline", "value": "30 days"}]
    card = build_detail_card(title="Rights", summary_rows=rows)
    assert card["title"] == "Rights"
    assert len(card["ctas"]) == 1
    assert card["ctas"][0]["selection"]["action"] == "proceed_to_draft"


def test_parse_selection_json():
    raw_json = '{"action": "submit_case_facts", "company": "Flipkart", "order_ref": "OD123"}'
    parsed = parse_selection(raw_json)
    assert parsed["action"] == "submit_case_facts"
    assert parsed["company"] == "Flipkart"
    assert parsed["order_ref"] == "OD123"


def test_parse_selection_prose_fallback():
    prose = "The user approved the draft to dispatch."
    parsed = parse_selection(prose)
    assert parsed.get("action") == "approve_dispatch"


def test_build_strength_and_edaakhil_cards():
    from common.cards import (
        build_edaakhil_card,
        build_health_card,
        build_reply_decision_card,
        build_strength_card,
    )
    facts = {"company": "Flipkart", "amount_inr": 24999.0}
    strength = {
        "merit_score": 94,
        "grade": "Strong Statutory Merit",
        "forum": "District Consumer Commission",
        "forum_rule": "Rules 2021",
        "violations": ["Rule 4(5)"],
        "missing_evidence": ["Invoice"],
    }
    scard = build_strength_card(facts, strength)
    assert "Legal Assessment" in scard["title"]
    assert scard["approve_cta"]["selection"]["action"] == "proceed_to_draft"

    ecard = build_edaakhil_card("REC-TEST", {"forum": "District Commission", "merit_score": 94, "annexures": [{"title": "A-1"}]})
    assert ecard["title"].startswith("e-Daakhil")

    hcard = build_health_card([{"name": "Concierge", "status": "ONLINE", "latency": "12ms"}])
    assert "System Health" in hcard["title"]

    rcard = build_reply_decision_card("REC-TEST", "Flipkart", {"sentiment": "rejected", "recommended_action": "rebuttal", "reasoning": "Doorstep void"}, "Send Rebuttal", "send_rebuttal")
    assert rcard["title"].startswith("Decision Loop")

