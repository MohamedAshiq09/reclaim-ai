import json
import time
from common.db import (
    get_active_case_for_user,
    get_case,
    get_case_events,
    init_db,
    list_due_waiting_cases,
    mark_tracking_paid,
    record_event,
    save_case,
    update_case_status,
)


def test_db_lifecycle():
    init_db()
    case_id = f"TEST-{int(time.time())}"
    user_addr = "agent1test_user_address_001"

    facts = {
        "company": "Flipkart",
        "order_ref": "OD999",
        "amount_inr": 12000.0,
        "issue_summary": "Defective item",
    }

    # Save
    save_case(
        case_id=case_id,
        user_addr=user_addr,
        category="ecommerce",
        company="Flipkart",
        facts_json=json.dumps(facts),
        status="INTAKE",
        deadline_at=time.time() + 10.0,
    )

    c = get_case(case_id)
    assert c is not None
    assert c["company"] == "Flipkart"
    assert c["status"] == "INTAKE"

    # Event recording
    record_event(case_id, "TEST_EVENT", "Recorded test event successfully")
    events = get_case_events(case_id)
    assert len(events) >= 1
    assert events[-1]["kind"] == "TEST_EVENT"

    # Status update
    update_case_status(case_id, status="WAITING", tier=1, email_msg_id="email_abc")
    updated = get_case(case_id)
    assert updated["status"] == "WAITING"
    assert updated["email_msg_id"] == "email_abc"

    # Active case retrieval
    active = get_active_case_for_user(user_addr)
    assert active is not None
    assert active["id"] == case_id

    # Mark paid
    mark_tracking_paid(case_id)
    paid_c = get_case(case_id)
    assert paid_c["tracking_paid"] == 1
