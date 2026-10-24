#!/usr/bin/env python3
from __future__ import annotations

import json
import time
from common.db import init_db, record_event, save_case

if __name__ == "__main__":
    init_db()

    case_id = "REC-DEMO2026"
    user_addr = "agent1q2a0f0a8zyw3229agt7saxtvenftxwe0gry6nv02dzd78rvye98tzty77e7"

    facts = {
        "case_id": case_id,
        "category": "ecommerce",
        "company": "Flipkart",
        "order_ref": "OD49281749102",
        "amount_inr": 24999.0,
        "order_date": "2026-10-18",
        "issue_summary": "Delivered Samsung Galaxy phone with shattered screen; Flipkart customer care refused refund claiming outer box intact.",
        "company_response": "Return rejected by seller citing delivery checklist.",
        "desired_outcome": "Immediate full refund of INR 24,999 to original bank account",
        "user_name": "Mohamed Ashiq",
        "user_email": "consumer.demo@example.com",
    }

    # Save case in WAITING state with deadline due in 15 seconds for live demonstration
    now = time.time()
    save_case(
        case_id=case_id,
        user_addr=user_addr,
        category="ecommerce",
        company="Flipkart",
        facts_json=json.dumps(facts),
        status="WAITING",
        deadline_at=now + 15.0,  # Firing in 15 seconds!
        tier=1,
        email_msg_id="resend_demo_initial_notice_123",
        tracking_paid=1,
    )

    record_event(case_id, "INTAKE_COMPLETED", "Form card submitted by user")
    record_event(case_id, "LEGAL_RESEARCH_DONE", "Identified Rule 5(4) E-Commerce Rules & Section 2(11) CPA 2019")
    record_event(case_id, "DRAFT_APPROVED", "User approved formal legal notice to Flipkart Grievance Officer")
    record_event(case_id, "NOTICE_DISPATCHED", "Email notice served on grievance.officer@flipkart.com (msg_id=resend_demo_initial_notice_123)")
    record_event(case_id, "WATCHER_ARMED", "Autonomous Watcher armed with accelerated demo deadline (15s)")

    print(f"✅ Successfully seeded demo case #{case_id} into cases.db!")
    print(f"Target company: {facts['company']}")
    print(f"Disputed amount: INR {facts['amount_inr']}")
    print("Deadline is set to trigger in 15 seconds to demonstrate Autonomous Watcher escalation.")
