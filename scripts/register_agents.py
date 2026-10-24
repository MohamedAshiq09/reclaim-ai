#!/usr/bin/env python3
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from uagents.agent import register_in_agentverse
from uagents.mailbox import AgentverseConnectRequest
from uagents_core.registration import AgentProfile, RegistrationRequest

from agents.concierge import agent as concierge_agent
from agents.researcher import agent as researcher_agent
from agents.drafter import agent as drafter_agent
from agents.dispatcher import agent as dispatcher_agent
from agents.watcher import agent as watcher_agent
from common.config import AGENTVERSE_API_KEY

BADGES = (
    "![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)\n"
    "![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)\n\n"
)

AGENTS_METADATA = [
    {
        "agent": concierge_agent,
        "name": "ReclaimAI Concierge",
        "handle": "reclaim-ai",
        "description": (
            "Autonomous Consumer Rights & Grievance Redressal Orchestrator for India. "
            "Researches consumer rights under CPA 2019 and E-Commerce Rules, finds Grievance Officers, "
            "drives ASI:One Interactive Cards, and executes autonomous Tier-2 escalations."
        ),
        "readme": (
            BADGES
            + "# ReclaimAI Concierge Agent\n\n"
            + "Primary orchestrator for ReclaimAI inside ASI:One. Handles intent understanding, "
            + "drives interactive Form/Detail/Review cards, and connects to the Fetch.ai Payment Protocol.\n\n"
            + f"**Address**: `{concierge_agent.address}`\n"
        ),
        "starter_prompts": [
            "Flipkart delivered a broken phone and refused my refund",
            "IndiGo flight cancelled refund not credited",
            "Dispute unauthorized bank transaction charges",
            "/status",
        ],
    },
    {
        "agent": researcher_agent,
        "name": "ReclaimAI Researcher",
        "handle": "reclaim-researcher",
        "description": (
            "Statutory consumer law researcher for India. Retrieves Consumer Protection Act 2019 provisions, "
            "E-Commerce Rules 2020 (Rule 4(4) & 4(5)), DGCA CAR Section 3 Series M Part II, and RBI Ombudsman Scheme."
        ),
        "readme": (
            BADGES
            + "# ReclaimAI Researcher Agent\n\n"
            + "Statutory rights and corporate nodal officer lookup agent.\n\n"
            + f"**Address**: `{researcher_agent.address}`\n"
        ),
        "starter_prompts": [
            "What are my rights under Rule 4(5) of E-Commerce Rules?",
            "What is the DGCA refund timeline for cancelled flights?",
        ],
    },
    {
        "agent": drafter_agent,
        "name": "ReclaimAI Drafter",
        "handle": "reclaim-drafter",
        "description": (
            "Statutory notice drafter for Indian consumer disputes. Formulates formal legal notices citing "
            "the Consumer Protection Act 2019 with statutory deadlines and CCPA / e-Daakhil warnings."
        ),
        "readme": (
            BADGES
            + "# ReclaimAI Drafter Agent\n\n"
            + "Formal legal notice drafting agent using ASI:One LLM.\n\n"
            + f"**Address**: `{drafter_agent.address}`\n"
        ),
        "starter_prompts": [
            "Draft a formal grievance notice for a defective smartphone delivery",
        ],
    },
    {
        "agent": dispatcher_agent,
        "name": "ReclaimAI Dispatcher",
        "handle": "reclaim-dispatcher",
        "description": (
            "Official notice transmission agent. Dispatches verified emails to corporate grievance officers "
            "via Resend API with exponential backoff and safe demo redirection."
        ),
        "readme": (
            BADGES
            + "# ReclaimAI Dispatcher Agent\n\n"
            + "Notice delivery and tracking agent.\n\n"
            + f"**Address**: `{dispatcher_agent.address}`\n"
        ),
        "starter_prompts": [],
    },
    {
        "agent": watcher_agent,
        "name": "ReclaimAI Escalation Watcher",
        "handle": "reclaim-watcher",
        "description": (
            "Autonomous deadline surveillance agent. Tracks statutory redressal timelines on interval, "
            "and autonomously files Tier-2 escalations to the National Consumer Helpline (NCH) and Regulatory Ombudsman."
        ),
        "readme": (
            BADGES
            + "# ReclaimAI Escalation Watcher Agent\n\n"
            + "Autonomous interval-based case tracking and escalation agent.\n\n"
            + f"**Address**: `{watcher_agent.address}`\n"
        ),
        "starter_prompts": [
            "Check active case deadlines and escalation status",
        ],
    },
]


async def register_all():
    if not AGENTVERSE_API_KEY:
        print("❌ Error: AGENTVERSE_API_KEY is not set in .env")
        sys.exit(1)

    print("=" * 70)
    print("📡 Registering all 5 ReclaimAI Agents on Agentverse...")
    print("=" * 70)

    connect_req = AgentverseConnectRequest(
        user_token=AGENTVERSE_API_KEY,
        agent_type="mailbox",
        endpoint=None,
    )

    for item in AGENTS_METADATA:
        ag = item["agent"]
        name = item["name"]
        print(f"Registering {name} ({ag.address})...")

        avatar = "https://storage.googleapis.com/agentverse-prod-assets/agent-avatars-pub/65049396.jpg"
        handle = item.get("handle")

        profile = AgentProfile(
            description=item["description"],
            readme=item["readme"],
            avatar_url=avatar,
            banner_url="",
            starter_prompts=item.get("starter_prompts", []),
        )

        reg_data = RegistrationRequest(
            address=ag.address,
            name=name,
            handle=handle,
            url=None,
            profile=profile,
            endpoints=ag._endpoints,
            protocols=list(ag.protocols.keys()),
            metadata=ag.metadata,
        )

        try:
            resp = await register_in_agentverse(
                request=connect_req,
                identity=ag._identity,
                prefix=ag._prefix,
                agentverse=ag._agentverse,
                agent_details=reg_data,
            )
            if resp.success:
                print(f"  ✅ {name} registered successfully on Agentverse!")
            else:
                print(f"  ⚠️ {name} response: {resp.detail}")
        except Exception as e:
            print(f"  ❌ Error registering {name}: {e}")

    print("=" * 70)
    print("🎉 All 5 ReclaimAI agents are registered on Agentverse!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(register_all())
