from __future__ import annotations

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

from common.config import (
    AGENTVERSE_API_KEY,
    RESEARCHER_ADDRESS,
    RESEARCHER_SEED,
    SEARCH_API_KEY,
)
from common.logging import log_inbound, log_outbound, log_state
from common.models import Citation, ResearchRequest, ResearchResult

# Curated, verified repository of Indian grievance contacts
COMPANY_CONTACTS = {
    "flipkart": {
        "name": "Flipkart Internet Private Limited",
        "email": "grievance.officer@flipkart.com",
        "url": "https://www.flipkart.com/pages/grievance-redressal",
        "verified": True,
    },
    "amazon": {
        "name": "Amazon Seller Services Private Limited",
        "email": "grievance-officer@amazon.in",
        "url": "https://www.amazon.in/gp/help/customer/display.html?nodeId=202111950",
        "verified": True,
    },
    "myntra": {
        "name": "Myntra Designs Private Limited",
        "email": "grievance@myntra.com",
        "url": "https://www.myntra.com/faqs#grievance",
        "verified": True,
    },
    "indigo": {
        "name": "InterGlobe Aviation Limited (IndiGo)",
        "email": "nodal.officer@goindigo.in",
        "url": "https://www.goindigo.in/contact-us/grievance-redressal.html",
        "verified": True,
    },
    "air india": {
        "name": "Air India Limited",
        "email": "nodal@airindia.com",
        "url": "https://www.airindia.com/in/en/contact-us/grievance-redressal.html",
        "verified": True,
    },
    "spicejet": {
        "name": "SpiceJet Limited",
        "email": "nodalofficer@spicejet.com",
        "url": "https://www.spicejet.com/GrievanceRedressal.aspx",
        "verified": True,
    },
    "hdfc": {
        "name": "HDFC Bank Limited",
        "email": "pno@hdfcbank.com",
        "url": "https://www.hdfcbank.com/personal/need-help/grievance-redressal-mechanism",
        "verified": True,
    },
    "sbi": {
        "name": "State Bank of India",
        "email": "agmcustomer.lho@sbi.co.in",
        "url": "https://sbi.co.in/web/customer-care/grievance-redressal",
        "verified": True,
    },
    "icici": {
        "name": "ICICI Bank Limited",
        "email": "headservicequality@icicibank.com",
        "url": "https://www.icicibank.com/complaints/grievance-redressal",
        "verified": True,
    },
    "airtel": {
        "name": "Bharti Airtel Limited",
        "email": "appellate.authority@airtel.com",
        "url": "https://www.airtel.in/grievance-redressal",
        "verified": True,
    },
    "jio": {
        "name": "Reliance Jio Infocomm Limited",
        "email": "appellate.officer@jio.com",
        "url": "https://www.jio.com/en-in/grievance-officer",
        "verified": True,
    },
}


def lookup_company_contact(company_name: str) -> dict[str, str]:
    cleaned = company_name.strip().lower()
    for key, val in COMPANY_CONTACTS.items():
        if key in cleaned:
            return val

    # Fallback heuristic
    slug = cleaned.replace(" ", "")
    return {
        "name": company_name,
        "email": f"grievance@{slug}.com",
        "url": f"https://www.{slug}.com/grievance-officer",
        "verified": False,
    }


def analyze_rights_and_laws(category: str) -> tuple[str, int, str, str, list[Citation]]:
    cat = category.lower().strip()
    citations: list[Citation] = []

    if cat == "airline":
        deadline_days = 7
        summary = (
            "Under DGCA CAR Section 3, Series M, Part II, airlines must process refunds for credit card cancellations "
            "within 7 working days (or immediately for cash). Booking portals/agents must disburse within 14 working days. "
            "Under Part IV, passengers are entitled to compensation and facilities for cancellations or delays."
        )
        next_tier = "AirSewa Portal (Ministry of Civil Aviation) & NCH"
        next_how = "File grievance at airsewa.gov.in or National Consumer Helpline (1915)"
        citations.append(
            Citation(
                title="DGCA CAR Section 3, Series M, Part II",
                url="https://www.dgca.gov.in",
                section="Part II, Para 3.3.2 (Refund of Airline Tickets)",
                note="Mandates ticket refund within 7 working days for credit cards and 14 days for agent bookings.",
            )
        )
        citations.append(
            Citation(
                title="Consumer Protection Act, 2019",
                url="https://consumeraffairs.nic.in",
                section="Section 2(11)",
                note="Arbitrary cancellation or non-refund constitutes statutory deficiency of service.",
            )
        )
    elif cat == "bank":
        deadline_days = 30
        summary = (
            "Under the Reserve Bank - Integrated Ombudsman Scheme 2021 (RB-IOS), the bank has 30 days to resolve "
            "unauthorized debit, failed UPI transactions, or disputed charges. If unresolved within 30 days or rejected, "
            "the consumer has the right to escalate directly to the RBI Ombudsman for refund and compensation."
        )
        next_tier = "RBI Integrated Ombudsman (CMS)"
        next_how = "Lodge complaint on RBI Complaint Management System at cms.rbi.org.in"
        citations.append(
            Citation(
                title="RBI Integrated Ombudsman Scheme, 2021",
                url="https://cms.rbi.org.in",
                section="Section 8 & 11",
                note="Single-window redressal for banks/NBFCs/UPI payment service providers.",
            )
        )
        citations.append(
            Citation(
                title="Consumer Protection Act, 2019",
                url="https://consumeraffairs.nic.in",
                section="Section 2(47)",
                note="Unilateral debit or refusing chargeback without fair investigation.",
            )
        )
    elif cat in ("telecom", "recharge"):
        deadline_days = 15
        summary = (
            "Under TRAI Consumer Protection Regulations, telecom service providers must resolve billing and recharge "
            "disputes within statutory deadlines. Unresolved complaints proceed to the Appellate Authority and NCH."
        )
        next_tier = "TRAI Telecom Appellate Authority & NCH"
        next_how = "Escalate to the Appellate Authority within 30 days or file at consumerhelpline.gov.in"
        citations.append(
            Citation(
                title="Telecom Consumer Protection Regulations (TRAI)",
                url="https://www.trai.gov.in",
                section="Regulation 12",
                note="Appellate mechanism for telecom grievances.",
            )
        )
    else:  # E-commerce default
        deadline_days = 30
        summary = (
            "Under Rule 4(4) and Rule 4(5) of the Consumer Protection (E-Commerce) Rules, 2020, every e-commerce entity is legally mandated "
            "to appoint a Grievance Officer, acknowledge receipt of any consumer grievance within 48 hours, and redress it within 1 month. "
            "Delivering damaged goods or refusing a refund is an unfair trade practice under Section 2(47) and deficiency of service under Section 2(11)."
        )
        next_tier = "National Consumer Helpline (NCH) & e-Daakhil"
        next_how = "File on consumerhelpline.gov.in (Toll-free 1915) or e-Daakhil portal (edaakhil.nic.in)"
        citations.append(
            Citation(
                title="Consumer Protection (E-Commerce) Rules, 2020",
                url="https://consumeraffairs.nic.in/acts-and-rules/consumer-protection/consumer-protection-e-commerce-rules-2020",
                section="Rule 4(4) & Rule 4(5) - Grievance Redressal Mechanism",
                note="Mandates appointment of Grievance Officer, 48-hour acknowledgment, and 30-day final redressal.",
            )
        )
        citations.append(
            Citation(
                title="Consumer Protection Act, 2019",
                url="https://consumeraffairs.nic.in",
                section="Section 2(9) & Section 35",
                note="Guarantees consumer right to seek redressal and direct filing via e-Daakhil.",
            )
        )


    return summary, deadline_days, next_tier, next_how, citations


def perform_research(case_id: str, category: str, company: str) -> ResearchResult:
    contact = lookup_company_contact(company)
    rights_summary, deadline_days, next_tier, next_how, citations = analyze_rights_and_laws(category)

    return ResearchResult(
        case_id=case_id,
        rights_summary=rights_summary,
        company_deadline_days=deadline_days,
        grievance_email=contact["email"],
        grievance_source_url=contact["url"],
        next_tier_name=next_tier,
        next_tier_how=next_how,
        citations=citations,
        ok=True,
    )


# Initialize Agent
agent = Agent(
    name="reclaimai_researcher",
    seed=RESEARCHER_SEED,
    port=8002,
    endpoint=None if AGENTVERSE_API_KEY else ["http://127.0.0.1:8002/submit"],
    mailbox=bool(AGENTVERSE_API_KEY),

    agentverse="https://agentverse.ai",
    network="testnet",
)

if os.getenv("TESTING") != "1" and agent.wallet:
    fund_agent_if_low(str(agent.wallet.address()))


# Protocol for inter-agent communication
research_proto = Protocol(name="research_protocol", version="1.0")


@research_proto.on_message(ResearchRequest)
async def handle_research_request(ctx: Context, sender: str, msg: ResearchRequest):
    log_inbound(ctx, "ResearchRequest", sender, f"case_id={msg.facts.case_id}")
    res = perform_research(
        case_id=msg.facts.case_id,
        category=msg.facts.category,
        company=msg.facts.company,
    )
    log_outbound(ctx, "ResearchResult", sender, f"case_id={res.case_id} email={res.grievance_email}")
    await ctx.send(sender, res)


# Also support standard Chat Protocol for direct queries and testing
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
            txt = item.text or ""
            res = perform_research("direct_query", "ecommerce", txt)
            reply = create_text_chat(
                f"ReclaimAI Legal Rights Summary:\n{res.rights_summary}\n\n"
                f"Statutory Deadline: {res.company_deadline_days} days\n"
                f"Next Escalation Tier: {res.next_tier_name}\n"
                f"Grievance Contact: {res.grievance_email} ({res.grievance_source_url})"
            )
            log_outbound(ctx, "ChatMessage", sender, f"reply={reply.msg_id}")
            await ctx.send(sender, reply)
        elif isinstance(item, EndSessionContent):
            log_state(ctx, "session_ended", f"sender={sender}")


@chat_proto.on_message(ChatAcknowledgement)
async def handle_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log_inbound(ctx, "ChatAcknowledgement", sender, f"ack_msg_id={msg.acknowledged_msg_id}")


agent.include(research_proto)
agent.include(chat_proto, publish_manifest=True)

if __name__ == "__main__":
    agent.run()
