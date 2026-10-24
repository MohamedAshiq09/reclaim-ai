from __future__ import annotations

import re
from datetime import datetime
from common.llm import clean_and_validate_notice, deterministic_draft, heuristic_extraction
from common.models import CaseFacts, Citation, ResearchResult


def test_clean_and_validate_notice_replaces_placeholders():
    raw_subj = "FORMAL GRIEVANCE NOTICE: [Company Name] - Order [Order ID]"
    raw_body = """Date: [DD/MM/YYYY]
To: The Grievance Officer, [Company Name]

I, [Your Name], residing at [Your Address], phone [Your Phone], register my grievance.
Regarding Order: [Order ID] for amount [Amount].

Facts: [...] Package received broken.

Yours sincerely,
[Your Name]
(Complainant)
"""
    facts = {
        "company": "Flipkart",
        "order_ref": "OD998877",
        "amount_inr": 24999.0,
        "user_name": "Mohamed Ashiq",
        "user_phone": "+91 98765 43210",
        "user_address": "Bengaluru, Karnataka",
        "user_email": "mohamedashiq782@gmail.com",
    }

    clean_subj, clean_body, ok = clean_and_validate_notice(raw_subj, raw_body, facts)

    assert ok is True
    assert "Flipkart" in clean_subj
    assert "OD998877" in clean_subj
    # Date must be real date, not [DD/MM/YYYY]
    today_str = datetime.now().strftime("%d %B %Y")
    assert today_str in clean_body
    assert "Mohamed Ashiq" in clean_body
    assert "Bengaluru, Karnataka" in clean_body
    assert "+91 98765 43210" in clean_body
    # ZERO bracketed placeholders allowed
    bracket_matches = re.findall(r"\[.*?\]", clean_body)
    assert bracket_matches == [], f"Found lingering bracketed placeholders: {bracket_matches}"
    assert "[" not in clean_body and "]" not in clean_body


def test_deterministic_draft_zero_placeholders():
    facts = {
        "company": "Flipkart",
        "order_ref": "OD123",
        "amount_inr": 24999.0,
        "issue_summary": "Delivered cracked screen and refused refund.",
        "user_name": "Mohamed Ashiq",
        "user_phone": "+91 98765 43210",
        "user_address": "Bengaluru, Karnataka",
        "user_email": "mohamedashiq782@gmail.com",
    }
    research = {
        "rights_summary": "Mandatory 48h ACK and 30-day resolution under Rule 4(5).",
        "citations": [
            {"title": "Consumer Protection (E-Commerce) Rules, 2020", "url": "https://consumeraffairs.nic.in", "note": "Rule 4(4) & 4(5)"}
        ],
    }

    draft = deterministic_draft(facts, research, tier=1)
    body = draft["body"]
    subj = draft["subject"]

    # Date check
    assert "Date:" in body
    assert datetime.now().strftime("%d %B %Y") in body

    # Complainant check
    assert "Mohamed Ashiq" in body
    assert "+91 98765 43210" in body
    assert "Bengaluru, Karnataka" in body

    # Bracket check
    assert re.findall(r"\[.*?\]", body) == []
    assert re.findall(r"\[.*?\]", subj) == []

    # Word count check (< 350 words)
    words = len(body.split())
    assert words < 350, f"Draft too long: {words} words"


def test_heuristic_extraction_parses_contact_info():
    text = (
        "Flipkart delivered a broken phone worth Rs 24999 order OD123. "
        "My name is Rajesh Sharma, contact: 9876543210, address: Mumbai, Maharashtra, email: rajesh@example.com"
    )
    facts = heuristic_extraction(text)
    assert facts["company"] == "Flipkart"
    assert facts["amount_inr"] == 24999.0
    assert facts["order_ref"] == "OD123"
    assert "Rajesh Sharma" in facts["user_name"]
    assert "9876543210" in facts["user_phone"]
    assert "Mumbai" in facts["user_address"]
    assert "rajesh@example.com" in facts["user_email"]
