from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4
import resend
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
from common.config import (
    AGENTVERSE_API_KEY,
    DEMO_MODE,
    DEMO_RECIPIENT_OVERRIDE,
    DISPATCHER_ADDRESS,
    DISPATCHER_SEED,
    FROM_EMAIL,
    RESEND_API_KEY,
)
from common.logging import log_error, log_inbound, log_outbound, log_state, log_timing
from common.models import DispatchRequest, DispatchResult

agent = Agent(
    name="reclaimai_dispatcher",
    seed=DISPATCHER_SEED,
    port=8004,
    endpoint=None if AGENTVERSE_API_KEY else ["http://127.0.0.1:8004/submit"],
    mailbox=bool(AGENTVERSE_API_KEY),

    agentverse="https://agentverse.ai",
    network="testnet",
)

if os.getenv("TESTING") != "1" and agent.wallet:
    fund_agent_if_low(str(agent.wallet.address()))


if RESEND_API_KEY:
    resend.api_key = RESEND_API_KEY

# Hard cap for the blocking Resend HTTP call so a slow email provider can
# never freeze the shared Bureau event loop.
SEND_TIMEOUT_S = 15.0


async def send_email_with_retry(
    to_email: str,
    cc_email: str,
    subject: str,
    body: str,
    retries: int = 3,
) -> tuple[bool, str | None, str | None]:
    """Send formal email notice via Resend with exponential backoff and demo override safety."""
    final_to = to_email
    prefix = ""

    if DEMO_MODE and DEMO_RECIPIENT_OVERRIDE:
        final_to = DEMO_RECIPIENT_OVERRIDE
        prefix = (
            f"[DEMO_MODE ACTIVE: Original Recipient={to_email}, CC={cc_email}]\n"
            f"--------------------------------------------------\n\n"
        )

    full_body = prefix + body

    if not RESEND_API_KEY:
        # Graceful simulation fallback
        msg_id = f"sim_{uuid4().hex[:12]}"
        return True, msg_id, None

    for attempt in range(1, retries + 1):
        try:
            params: resend.Emails.SendParams = {
                "from": FROM_EMAIL,
                "to": [final_to],
                "subject": subject,
                "text": full_body,
            }
            if cc_email and not DEMO_MODE:
                params["cc"] = [cc_email]

            # resend.Emails.send is a blocking HTTP call: offload to a worker
            # thread with a hard timeout so the shared Bureau loop never freezes.
            response = await asyncio.wait_for(
                asyncio.to_thread(resend.Emails.send, params),
                timeout=SEND_TIMEOUT_S,
            )
            msg_id = response.get("id") if isinstance(response, dict) else getattr(response, "id", str(uuid4()))
            return True, str(msg_id), None
        except Exception as e:
            if attempt == retries:
                return False, None, str(e)
            await asyncio.sleep(2**attempt)

    return False, None, "Max retries exceeded"


dispatch_proto = Protocol(name="dispatch_protocol", version="1.0")


@dispatch_proto.on_message(DispatchRequest)
async def handle_dispatch_request(ctx: Context, sender: str, msg: DispatchRequest):
    t0 = time.time()
    log_inbound(ctx, "DispatchRequest", sender, f"case_id={msg.case_id} to={msg.to_email}")

    # Strip any lingering bracket placeholders
    clean_body = msg.body
    if "[" in clean_body or "]" in clean_body:
        clean_body = clean_body.replace("[", "").replace("]", "")

    ok, message_id, err = await send_email_with_retry(
        to_email=msg.to_email,
        cc_email=msg.cc_email,
        subject=msg.subject,
        body=clean_body,
    )

    duration = time.time() - t0
    log_timing(ctx, "send", duration, msg.case_id)

    fallback_text = None if ok else f"Subject: {msg.subject}\n\n{clean_body}"

    res = DispatchResult(
        case_id=msg.case_id,
        ok=ok,
        message_id=message_id,
        fallback_text=fallback_text,
        error=err,
    )
    log_outbound(ctx, "DispatchResult", sender, f"case_id={res.case_id} ok={res.ok} msg_id={res.message_id}")
    await ctx.send(sender, res)


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
                "ReclaimAI Dispatcher Agent: I handle verified email dispatch to corporate grievance cells with "
                "safe demo routing and exponential backoff retry."
            )
            log_outbound(ctx, "ChatMessage", sender, f"reply={reply.msg_id}")
            await ctx.send(sender, reply)
        elif isinstance(item, EndSessionContent):
            log_state(ctx, "session_ended", f"sender={sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log_inbound(ctx, "ChatAcknowledgement", sender, f"ack_msg_id={msg.acknowledged_msg_id}")


agent.include(dispatch_proto)
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
