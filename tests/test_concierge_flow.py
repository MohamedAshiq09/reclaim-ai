"""End-to-end concierge chat-flow regression tests (offline, no network).

These cover the live ASI:One bug report raised 2026-10-24:
- T1: first complaint message no longer silently dies on save_case
- T2: rebuttal DispatchRequest constructs without the removed tier field
- T5: /ping and /cardtest respond instantly with text / a review card
- T6b: typed text equivalents route to the pending card action
- T7: an internal handler error still produces a friendly outbound text
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

import pytest
from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    MetadataContent,
    StartSessionContent,
    TextContent,
)

import common.db as db_mod
from agents import concierge as concierge_mod
from agents.concierge import handle_chat_message, handle_send_rebuttal
from common.models import DispatchRequest, ResearchRequest


class _Logger:
    def __init__(self, sink: list[str]) -> None:
        self._sink = sink

    def info(self, msg: str) -> None:
        self._sink.append(f"INFO {msg}")

    def error(self, msg: str) -> None:
        self._sink.append(f"ERROR {msg}")

    def warning(self, msg: str) -> None:
        self._sink.append(f"WARN {msg}")


class FakeCtx:
    """Minimal uAgents Context double: records sends, never raises."""

    def __init__(self) -> None:
        self.sent: list[tuple[str, Any]] = []
        self.logs: list[str] = []
        self.logger = _Logger(self.logs)

    async def send(self, target: str, message: Any) -> None:
        self.sent.append((target, message))


@pytest.fixture()
def tiny_db(tmp_path, monkeypatch):
    monkeypatch.setattr(db_mod, "DATABASE_PATH", tmp_path / "cases_test.db")
    db_mod.init_db()


@pytest.fixture()
def offline_llm(monkeypatch):
    monkeypatch.setattr("common.llm.ASI_ONE_API_KEY", "")


@pytest.fixture(autouse=True)
def reset_sessions():
    concierge_mod.active_sessions.clear()
    yield
    concierge_mod.active_sessions.clear()


def make_chat_message(text: str, start_session: bool = False) -> ChatMessage:
    content: list[Any] = []
    if start_session:
        content.append(StartSessionContent(type="start-session"))
    content.append(TextContent(type="text", text=text))
    return ChatMessage(timestamp=datetime.now(timezone.utc), msg_id=uuid4(), content=content)


def text_of(message: Any) -> str:
    return " ".join(c.text for c in message.content if isinstance(c, TextContent))


def run(ctx: FakeCtx, msg: ChatMessage) -> None:
    asyncio.run(handle_chat_message(ctx, "agent1q_dummy_sender", msg))


def test_first_complaint_message_full_flow(tiny_db, offline_llm, monkeypatch):
    """T1/T5: welcome AND complaint must both be processed on message one."""
    monkeypatch.setattr(db_mod, "DATABASE_PATH", db_mod.DATABASE_PATH)
    ctx = FakeCtx()
    run(ctx, make_chat_message(
        "Flipkart delivered a broken Samsung Galaxy phone worth Rs 24,999, "
        "order OD123, and refused my refund",
        start_session=True,
    ))

    targets = [t for t, _ in ctx.sent]
    assert all(t == "agent1q_dummy_sender" for t in targets)
    assert len(ctx.sent) >= 4, "expected ack + greeting + analysing text + intake card"

    kinds = [type(m).__name__ for _, m in ctx.sent]
    assert "ChatAcknowledgement" in kinds
    assert any(isinstance(m, ChatMessage) for _, m in ctx.sent)

    card_msgs = [
        m
        for _, m in ctx.sent
        if isinstance(m, ChatMessage) and any(isinstance(c, MetadataContent) for c in m.content)
    ]
    assert card_msgs, "intake review card was never sent"
    meta = next(c.metadata for c in card_msgs[-1].content if isinstance(c, MetadataContent))
    assert meta["card_kind"] == "review"
    assert meta["card_protocol_version"] == "1"
    payload_text = meta["card_payload"]
    assert "Grievance Intake Confirmation" in payload_text
    assert "Flipkart" in payload_text

    session = concierge_mod.active_sessions["agent1q_dummy_sender"]
    assert session["state"] == "FORM_PRESENTED"
    case_row = db_mod.get_case(session["case_id"])
    assert case_row is not None, "T1 regression: intake case was not persisted"
    assert case_row["company"] == "Flipkart"
    assert case_row["user_addr"] == "agent1q_dummy_sender"
    assert case_row["status"] == "INTAKE_CONFIRMATION"
    facts_json = case_row["facts_json"]
    assert facts_json and "broken Samsung Galaxy" in facts_json


def test_ping_instant_reply(tiny_db, offline_llm):
    """T5: /ping answers with text only, describing current state."""
    ctx = FakeCtx()
    run(ctx, make_chat_message("/ping"))
    assert len(ctx.sent) == 2  # ack + pong
    reply = ctx.sent[-1][1]
    assert not any(isinstance(c, MetadataContent) for c in reply.content)
    assert "pong" in text_of(reply)


def test_cardtest_sends_review_card(tiny_db, offline_llm):
    """T5: /cardtest renders a terminal review card on demand."""
    ctx = FakeCtx()
    run(ctx, make_chat_message("/cardtest"))
    reply = ctx.sent[-1][1]
    meta = next(c.metadata for c in reply.content if isinstance(c, MetadataContent))
    assert meta["card_kind"] == "review"
    assert meta["is_terminal"] == "true"
    assert "Simple Review" in meta['card_payload'] or "Card Diagnostic" in meta["card_payload"]


def test_typed_text_equivalents_route_to_pending_actions(
    tiny_db, offline_llm, monkeypatch
):
    """T6b: short replies route by session state without any JSON click."""
    monkeypatch.setattr("common.llm.ASI_ONE_API_KEY", "")
    # research not needed: submit_case_facts fires a ResearchRequest off-stage
    concierge_mod.active_sessions["agent1q_dummy_sender"] = {
        "case_id": "REC-TESTAA",
        "state": "FORM_PRESENTED",
        "facts": {
            "category": "ecommerce",
            "company": "Flipkart",
            "order_ref": "OD123",
            "amount_inr": 24999.0,
            "issue_summary": "broken phone refused refund",
        },
        "research": None,
        "draft": None,
    }
    ctx = FakeCtx()
    run(ctx, make_chat_message("1"))
    outbound_types = [type(m).__name__ for _, m in ctx.sent]
    assert "ResearchRequest" in outbound_types, "1 did not trigger submit_case_facts"
    assert concierge_mod.active_sessions["agent1q_dummy_sender"]["state"] == "RESEARCHING"

    # Retry in DRAFTING state re-runs the drafter request
    concierge_mod.active_sessions["agent1q_dummy_sender"]["state"] = "DRAFTING"
    ctx2 = FakeCtx()
    run(ctx2, make_chat_message("retry"))
    assert any(
        isinstance(m, concierge_mod.DraftRequest) for _, m in ctx2.sent  # type: ignore[attr-defined]
    )


def test_error_still_replies_friendly_text(tiny_db, offline_llm, monkeypatch):
    """T7: a handler crash must answer the user, never vanish into a spinner."""

    async def boom(*args: Any, **kwargs: Any) -> None:
        raise RuntimeError("synthetic failure for regression test")

    monkeypatch.setattr(concierge_mod, "handle_initial_complaint_intent", boom)
    ctx = FakeCtx()
    run(ctx, make_chat_message(
        "Flipkart delivered a broken Samsung Galaxy phone and refused my refund",
        start_session=True,
    ))
    error = [
        line for line in ctx.logs if "ERROR" in line
    ]
    assert error, "the failure was not logged through the structured logger"
    texts = [text_of(m) for _, m in ctx.sent if isinstance(m, ChatMessage)]
    assert any("failed at step" in t and "retry" in t for t in texts), texts


def test_rebuttal_dispatch_request_construction(tiny_db, offline_llm):
    """T2: handle_send_rebuttal must build DispatchRequest (no tier field)."""
    assert "tier" not in DispatchRequest.__fields__
    concierge_mod.active_sessions["agent1q_dummy_sender"] = {
        "case_id": "REC-TESTCC",
        "state": "REBUTTAL_PENDING",
        "facts": {"company": "Flipkart", "order_ref": "OD123", "user_email": "c@x.in"},
        "research": None,
        "draft": {"subject": "REBUTTAL NOTICE", "body": "statutory rebuttal body"},
    }
    ctx = FakeCtx()
    asyncio.run(handle_send_rebuttal(ctx, "agent1q_dummy_sender", concierge_mod.active_sessions["agent1q_dummy_sender"]))
    dispatched = [m for _, m in ctx.sent if isinstance(m, DispatchRequest)]
    assert dispatched, "T2 regression: rebuttal DispatchRequest never sent"
    assert dispatched[0].subject.startswith("REBUTTAL NOTICE")
    targets = [t for t, _ in ctx.sent]
    assert concierge_mod.DISPATCHER_ADDRESS in targets


def test_research_request_model_roundtrip(tiny_db, offline_llm):
    """Plumb-check the inter-agent request built inside the flow."""
    req = ResearchRequest(facts=concierge_mod.CaseFacts(  # type: ignore[attr-defined]
        case_id="REC-X", category="ecommerce", company="Flipkart", issue_summary="s"
    ))
    assert req.facts.company == "Flipkart"
