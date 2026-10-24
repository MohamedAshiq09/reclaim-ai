from __future__ import annotations

import asyncio
import os
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

import time
from common.config import AGENTVERSE_API_KEY, DRAFTER_ADDRESS, DRAFTER_SEED
from common.llm import generate_complaint_draft, deterministic_draft, clean_and_validate_notice
from common.logging import log_error, log_inbound, log_outbound, log_state, log_timing
from common.models import DraftRequest, DraftResult

# Draft generation hard timeout targeting <15s latency budget;
# a timeout still degrades to the deterministic statutory template.
DRAFT_TIMEOUT_S = float(os.getenv("DRAFT_TIMEOUT_S", "15"))

agent = Agent(
    name="reclaimai_drafter",
    seed=DRAFTER_SEED,
    port=8003,
    endpoint=None if AGENTVERSE_API_KEY else ["http://127.0.0.1:8003/submit"],
    mailbox=bool(AGENTVERSE_API_KEY),
    agentverse="https://agentverse.ai",
    network="testnet",
)

if os.getenv("TESTING") != "1" and agent.wallet:
    fund_agent_if_low(str(agent.wallet.address()))


draft_proto = Protocol(name="draft_protocol", version="1.0")


@draft_proto.on_message(DraftRequest)
async def handle_draft_request(ctx: Context, sender: str, msg: DraftRequest):
    t0 = time.time()
    log_inbound(ctx, "DraftRequest", sender, f"case_id={msg.facts.case_id} tier={msg.tier}")

    facts_dict = {
        "case_id": msg.facts.case_id,
        "category": msg.facts.category,
        "company": msg.facts.company,
        "order_ref": msg.facts.order_ref,
        "amount_inr": msg.facts.amount_inr,
        "issue_summary": msg.facts.issue_summary,
        "user_name": msg.facts.user_name,
        "user_email": msg.facts.user_email,
        "user_phone": msg.facts.user_phone,
        "user_address": msg.facts.user_address,
        "desired_outcome": msg.facts.desired_outcome,
    }

    research_dict = {
        "rights_summary": msg.research.rights_summary,
        "citations": [{"title": c.title, "url": c.url, "section": c.section, "note": c.note} for c in msg.research.citations],
        "company_deadline_days": msg.research.company_deadline_days,
        "grievance_email": msg.research.grievance_email,
    }

    try:
        res = await asyncio.wait_for(
            asyncio.to_thread(
                generate_complaint_draft,
                facts=facts_dict,
                research=research_dict,
                tier=msg.tier,
                feedback=msg.feedback,
            ),
            timeout=DRAFT_TIMEOUT_S,
        )
    except Exception as exc:
        log_error(ctx, f"draft generation degraded ({type(exc).__name__})", "using deterministic statutory template")
        res = deterministic_draft(facts=facts_dict, research=research_dict, tier=msg.tier)

    # Sanitize and strictly enforce zero bracketed placeholders
    clean_subj, clean_body, _ = clean_and_validate_notice(res["subject"], res["body"], facts_dict)

    duration = time.time() - t0
    log_timing(ctx, "draft", duration, msg.facts.case_id)

    out = DraftResult(
        case_id=msg.facts.case_id,
        subject=clean_subj,
        body=clean_body,
        tier=msg.tier,
        ok=True,
    )
    log_outbound(ctx, "DraftResult", sender, f"case_id={out.case_id} subject={out.subject[:50]}")
    await ctx.send(sender, out)


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
                "ReclaimAI Drafter Agent: I generate statutory legal notices citing the Consumer Protection Act, 2019 "
                "and sectoral regulations. Send me a dispute case to generate a formal notice."
            )
            log_outbound(ctx, "ChatMessage", sender, f"reply={reply.msg_id}")
            await ctx.send(sender, reply)
        elif isinstance(item, EndSessionContent):
            log_state(ctx, "session_ended", f"sender={sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log_inbound(ctx, "ChatAcknowledgement", sender, f"ack_msg_id={msg.acknowledged_msg_id}")


agent.include(draft_proto)
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
