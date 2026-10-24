from __future__ import annotations

import json
import os
import time

from datetime import datetime, timezone
from uuid import uuid4
from uagents import Agent, Context, Protocol
from uagents.setup import fund_agent_if_low
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    EndSessionContent,
    StartSessionContent,
    TextContent,
    chat_protocol_spec,
)

from common.config import (
    AGENTVERSE_API_KEY,
    CONCIERGE_ADDRESS,
    DISPATCHER_ADDRESS,
    DRAFTER_ADDRESS,
    WATCHER_ADDRESS,
    WATCHER_SEED,
)
from common.db import (
    get_case,
    init_db,
    list_due_waiting_cases,
    record_event,
    update_case_status,
)
from common.logging import log_error, log_inbound, log_outbound, log_state
from common.models import (
    CaseFacts,
    Citation,
    DispatchRequest,
    DispatchResult,
    DraftRequest,
    DraftResult,
    ResearchResult,
    WatcherEscalateTrigger,
    WatcherRegisterCase,
)

init_db()

agent = Agent(
    name="reclaimai_watcher",
    seed=WATCHER_SEED,
    port=8005,
    endpoint=None if AGENTVERSE_API_KEY else ["http://127.0.0.1:8005/submit"],
    mailbox=bool(AGENTVERSE_API_KEY),

    agentverse="https://agentverse.ai",
    network="testnet",
)

if os.getenv("TESTING") != "1" and agent.wallet:
    fund_agent_if_low(str(agent.wallet.address()))


watcher_proto = Protocol(name="watcher_protocol", version="1.0")


@watcher_proto.on_message(WatcherRegisterCase)
async def handle_register_case(ctx: Context, sender: str, msg: WatcherRegisterCase):
    log_inbound(ctx, "WatcherRegisterCase", sender, f"case_id={msg.case_id} deadline_seconds={msg.deadline_seconds}")
    deadline_ts = time.time() + msg.deadline_seconds
    update_case_status(msg.case_id, status="WAITING", deadline_at=deadline_ts)
    record_event(
        msg.case_id,
        "WATCHER_REGISTERED",
        f"Autonomous monitoring initiated. Next check at {time.strftime('%H:%M:%S', time.localtime(deadline_ts))}",
    )
    log_state(ctx, "case_watching", f"case_id={msg.case_id} deadline_ts={deadline_ts}")


@watcher_proto.on_message(DispatchResult)
async def handle_dispatch_result(ctx: Context, sender: str, msg: DispatchResult):
    log_inbound(ctx, "DispatchResult", sender, f"case_id={msg.case_id} ok={msg.ok}")
    if msg.ok:
        record_event(
            msg.case_id,
            "ESCALATION_EMAIL_SENT",
            f"Autonomous Tier-2 escalation email delivered (msg_id={msg.message_id})",
        )
    else:
        record_event(
            msg.case_id,
            "ESCALATION_EMAIL_FAILED",
            f"Dispatch error: {msg.error}",
        )


@agent.on_interval(period=15.0)
async def check_deadlines_and_escalate(ctx: Context):
    now_ts = time.time()
    due_cases = list_due_waiting_cases(now_ts)

    for c in due_cases:
        case_id = c["id"]
        company = c["company"]
        user_addr = c["user_addr"]
        facts = json.loads(c["facts_json"])

        ctx.logger.info(f"[watcher] Case #{case_id} deadline passed with no company resolution. Triggering AUTONOMOUS ESCALATION!")

        # Update status to ESCALATED in DB immediately to prevent double firing
        update_case_status(case_id, status="ESCALATED", tier=2)
        record_event(
            case_id,
            "AUTONOMOUS_ESCALATION_TRIGGERED",
            f"No resolution from {company} within statutory window. Escalating to Tier-2 Regulatory Redressal.",
        )

        # Formulate Tier-2 notice
        subject = f"STATUTORY ESCALATION TIER-2: Unresolved Grievance - {company} [Case #{case_id}]"
        body = (
            f"TO THE NATIONAL CONSUMER HELPLINE / REGULATORY OMBUDSMAN & {company.upper()} GRIEVANCE CELL:\n\n"
            f"RE: FORMAL ESCALATION OF UNRESOLVED CONSUMER DISPUTE\n"
            f"Complainant: {facts.get('user_name', 'Consumer')} ({facts.get('user_email', '')})\n"
            f"Disputed Entity: {company}\n"
            f"Order Reference: {facts.get('order_ref', 'N/A')}\n"
            f"Amount Claimed: INR {facts.get('amount_inr', 'Pending')}\n\n"
            f"FACTS:\n"
            f"A formal statutory grievance notice was served on {company}. The statutory timeline mandated under "
            f"the Consumer Protection (E-Commerce) Rules, 2020 / Sectoral Regulations has expired with zero or inadequate resolution.\n\n"
            f"RELIEF SOUGHT:\n"
            f"1. Order immediate refund of INR {facts.get('amount_inr', '')} plus interest.\n"
            f"2. Initiate regulatory inquiry under Section 20 of the Consumer Protection Act, 2019 for unfair trade practices.\n\n"
            f"-- Dispatched autonomously by ReclaimAI Watcher Agent"
        )

        dispatch_req = DispatchRequest(
            case_id=case_id,
            to_email="grievance@" + company.lower().replace(" ", "") + ".com",
            cc_email=facts.get("user_email", ""),
            subject=subject,
            body=body,
            request_id=f"esc_{case_id}_{int(now_ts)}",
        )

        log_outbound(ctx, "DispatchRequest", DISPATCHER_ADDRESS, f"case_id={case_id} tier=2")
        await ctx.send(DISPATCHER_ADDRESS, dispatch_req)


# Chat Protocol
chat_proto = Protocol(spec=chat_protocol_spec)


def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


@chat_proto.on_message(ChatMessage)
async def handle_chat_message(ctx: Context, sender: str, msg: ChatMessage):
    log_inbound(ctx, "ChatMessage", sender, f"msg_id={msg.msg_id}")
    ack = ChatAcknowledgement(timestamp=datetime.now(timezone.utc), acknowledged_msg_id=msg.msg_id)
    log_outbound(ctx, "ChatAcknowledgement", sender, f"ack={msg.msg_id}")
    await ctx.send(sender, ack)

    for item in msg.content:
        if isinstance(item, StartSessionContent):
            log_state(ctx, "session_started", f"sender={sender}")
        elif isinstance(item, TextContent):
            reply = create_text_chat(
                "ReclaimAI Escalation Watcher: I autonomously track case deadlines and file Tier-2 escalations "
                "to the National Consumer Helpline and Regulatory Ombudsman."
            )
            log_outbound(ctx, "ChatMessage", sender, f"reply={reply.msg_id}")
            await ctx.send(sender, reply)
        elif isinstance(item, EndSessionContent):
            log_state(ctx, "session_ended", f"sender={sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log_inbound(ctx, "ChatAcknowledgement", sender, f"ack_msg_id={msg.acknowledged_msg_id}")


agent.include(watcher_proto)
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
