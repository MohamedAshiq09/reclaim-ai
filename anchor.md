# ReclaimAI Anchor — Single Source of Truth

> **MANDATORY**: Any new agent or developer session working on this codebase **MUST read this file first** and update it before finishing.

---

## 1. Project Identity
- **Project Name**: ReclaimAI
- **Event**: Fetch-A-Thon 3.0 (Fetch.ai Innovation Lab)
- **Challenge Statement**: ASI:One Agent Challenge — From Intent to Action
- **Event Date**: October 24, 2026
- **Timeline (IST)**:
  - 10:30 IST — Building Begins
  - 13:00 IST — Lunch & Networking
  - 14:00 IST — Building Continues
  - 16:30 IST — Final Building & Submission Window Opens
  - 17:50 IST — Final Submission Closes
  - 18:00 IST — Event Ends

---

## 2. Deliverables Status Table

| Deliverable | Status | Link / Reference | Notes |
| :--- | :--- | :--- | :--- |
| **Public GitHub Repository** | **IN PROGRESS** | https://github.com/MohamedAshiq09/reclaim-ai | Local git clean; initial commits pushed |
| **README Innovation Lab Badges** | **DONE** | [README.md](README.md) | `tag:innovationlab` and `tag:hackathon` included |
| **Agentverse Profile URLs** | **DONE** | See Section 3 below | All 5 agents registered on Agentverse |
| **Public ASI:One Shared Chat URL** | **NOT STARTED** | Pending user live chat run | Will generate from ASI:One chat interface |
| **Demo Video (3–5 min)** | **NOT STARTED** | Script ready in [docs/demo_script.md](docs/demo_script.md) | Recording scheduled for ~15:30 IST |
| **Dashboard Agent Submission** | **NOT STARTED** | Fetch-A-Thon 3.0 Dashboard | Mandatory via Project Submission Agent |

---

## 3. Agent Registry (All 5 Agents)

All 5 agents run on **Fetch.ai Testnet** with deterministic seeds:

| Agent Name | Deterministic Address | Source File | Agentverse Profile URL | Mailbox Status | Last Verified Time (IST) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **ReclaimAI Concierge** | `agent1q2a0f0a8zyw3229agt7saxtvenftxwe0gry6nv02dzd78rvye98tzty77e7` | `agents/concierge.py` | https://agentverse.ai/agents/details/agent1q2a0f0a8zyw3229agt7saxtvenftxwe0gry6nv02dzd78rvye98tzty77e7 | **Active** (Mailbox registered & polled) | 2026-10-24 10:44 |
| **ReclaimAI Researcher** | `agent1qgktn2gauj62w4uaynnapajvsexxjgxuq8ylj6ru2503p9hxt09h6tcgaum` | `agents/researcher.py` | https://agentverse.ai/agents/details/agent1qgktn2gauj62w4uaynnapajvsexxjgxuq8ylj6ru2503p9hxt09h6tcgaum | **Active** (Mailbox registered) | 2026-10-24 10:44 |
| **ReclaimAI Drafter** | `agent1q00z4x9d574zttujnjwkj7zz7u0elv4jw4exrrefvqegjnz0dntu5cj5js0` | `agents/drafter.py` | https://agentverse.ai/agents/details/agent1q00z4x9d574zttujnjwkj7zz7u0elv4jw4exrrefvqegjnz0dntu5cj5js0 | **Active** (Mailbox registered) | 2026-10-24 10:44 |
| **ReclaimAI Dispatcher** | `agent1qg9evq8equ7kkt2nw8fkg2wgujr6sy69ucpeflyr28539rnx8v7ng2wuu8l` | `agents/dispatcher.py` | https://agentverse.ai/agents/details/agent1qg9evq8equ7kkt2nw8fkg2wgujr6sy69ucpeflyr28539rnx8v7ng2wuu8l | **Active** (Mailbox registered) | 2026-10-24 10:44 |
| **ReclaimAI Escalation Watcher** | `agent1qgz54hf8dzdvqsuf3ja9vfvdl25d9umed0r6y6vhalwtl2s0vqkmw3l0a46` | `agents/watcher.py` | https://agentverse.ai/agents/details/agent1qgz54hf8dzdvqsuf3ja9vfvdl25d9umed0r6y6vhalwtl2s0vqkmw3l0a46 | **Active** (Mailbox registered) | 2026-10-24 10:44 |

---

## 4. Environment Variables Checklist

| Env Variable | Status in `.env` | Purpose |
| :--- | :--- | :--- |
| `AGENTVERSE_API_KEY` | **SET** | Mailbox creation and Agentverse discovery |
| `ASI_ONE_API_KEY` | **SET** | Real ASI:One LLM intent extraction and legal drafting |
| `SEARCH_API_KEY` | **UNSET** (Optional) | Live search; system uses verified curated table for top 10 companies |
| `RESEND_API_KEY` | **UNSET** (Optional) | Real email sending; falls back gracefully to safe internal simulation |
| `FROM_EMAIL` | **SET** (`onboarding@resend.dev`) | Sender address for Resend notices |
| `DEMO_MODE` | **SET** (`1`) | Enables demo email override and accelerates deadlines to ~120s |
| `DEMO_RECIPIENT_OVERRIDE` | **UNSET** | Personal inbox to receive test notices safely |
| `FET_USE_TESTNET` | **SET** (`true`) | Native FET on-chain payments via testnet (`atestfet`) |
| `FET_PAYMENT_AMOUNT` | **SET** (`0.001`) | Price in FET for the auto-escalation & tracking pack |
| Seeds (`CONCIERGE_SEED`, etc.) | **SET** | Deterministic cryptographic agent address generation |
| Addresses (`CONCIERGE_ADDRESS`, etc.) | **SET** | Inter-agent message routing |

---

## 5. Verified Facts Index

| Statutory Authority / Scheme | Exact Section / Rule | Key Verified Fact | Official Source URL | Verified Date | Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Consumer Protection (E-Commerce) Rules, 2020** | **Rule 4(4) & Rule 4(5)** | Grievance Officer appointment mandatory under 4(4); 48h acknowledgment and 30-day final redressal mandatory under 4(5). (NOT Rule 5(4)). | https://consumeraffairs.nic.in/acts-and-rules/consumer-protection/consumer-protection-e-commerce-rules-2020 | 2026-10-24 | **VERIFIED** |
| **Consumer Protection Act, 2019** | **Section 2(9), 2(11), 2(47)** | Statutory rights against unfair trade practices and service deficiency. Unilateral refund rejections prohibited. | https://consumeraffairs.nic.in | 2026-10-24 | **VERIFIED** |
| **Consumer Commission Online Filing** | **Section 35 / e-Daakhil** | Digital complaint filing before Consumer Commissions without physical presence. | https://edaakhil.nic.in | 2026-10-24 | **VERIFIED** |
| **National Consumer Helpline** | **NCH / INGRAM (1915)** | Official portal for registering consumer grievances. | https://consumerhelpline.gov.in | 2026-10-24 | **VERIFIED** |
| **DGCA Airline Ticket Refunds** | **CAR Section 3, Series M, Part II (Para 3.3.2)** | 7-day refund for credit card cancellations; 14 working days for travel portal/agent bookings. (NOT Part IV). | https://www.dgca.gov.in | 2026-10-24 | **VERIFIED** |
| **DGCA Cancellation/Delay Compensation** | **CAR Section 3, Series M, Part IV** | Refreshments for delays >2h; ₹5,000–₹10,000 compensation for unnotified cancellations. | https://www.dgca.gov.in | 2026-10-24 | **VERIFIED** |
| **RBI Integrated Ombudsman Scheme 2021** | **Section 8 & 11** | Mandatory 30-day dispute window before bank; escalation to CMS portal with up to ₹20L compensation. | https://cms.rbi.org.in | 2026-10-24 | **VERIFIED** |
| **ASI:One Interactive Cards** | **ACP Metadata v1** | `card_protocol_version: "1"`, `card_kind`, `requires_card_interaction: "true"`, JSON `card_payload`. | https://docs.agentverse.ai/documentation/advanced-usages/predefined-card-schemas | 2026-10-24 | **VERIFIED** |
| **Fetch.ai Payment Protocol** | **`payment_protocol_spec`** | Native FET direct payment seller flow with cosmpy verification. | https://innovationlab.fetch.ai/resources/docs/agent-transaction/agent-payment-protocol | 2026-10-24 | **VERIFIED** |

---

## 6. Real vs Simulated/Faked Matrix

| Feature | Real or Simulated? | Details & Mitigation |
| :--- | :--- | :--- |
| **Agentverse Registration** | **REAL** | All 5 agents registered via API; mailboxes confirmed active (HTTP 200). |
| **ASI:One LLM Reasoning** | **REAL** | Connected to live `https://api.asi1.ai/v1` via valid `ASI_ONE_API_KEY`. |
| **Legal Corpus & Citations** | **REAL** | Verified against official gazettes; exact sections cited. |
| **Inter-Agent Communication** | **REAL** | Protocol models exchanging structured messages between agents. |
| **Interactive Cards** | **REAL** | Predefined card schemas conforming strictly to wire format. |
| **Email Notice Dispatch** | **SIMULATED** (if `RESEND_API_KEY` unset) | Without key, dispatcher logs and produces fallback text. With key, delivers via Resend API to `DEMO_RECIPIENT_OVERRIDE`. |
| **Live Contact Lookup** | **HYBRID** | Curated table of top 10 Indian enterprises (Flipkart, Amazon, IndiGo, HDFC, etc.) + fallback. |
| **Watcher Escalation** | **REAL** | `@on_interval` background loop fires on deadline and inserts events in `cases.db`. |
| **Payment Verification** | **REAL** | Uses `cosmpy` against testnet ledger with sandbox fallback. |

---

## 7. Decisions Log
1. **Rule 4(4) & 4(5) vs 5(4)**: Fixed citation from Rule 5(4) to Rule 4(4) & 4(5) of the E-Commerce Rules, 2020 because Rule 4 explicitly governs the Grievance Officer duties and timelines.
2. **DGCA Part II vs Part IV**: Fixed citation from Part IV to Part II (Para 3.3.2) for airline ticket refunds (7 days credit card, 14 days portal), reserving Part IV for cancellation/delay compensation.
3. **Mailbox vs Endpoint in uAgents**: Discovered that passing `endpoint` overrides and disables `mailbox=True`. Fixed all agents to set `endpoint=None` when `AGENTVERSE_API_KEY` is present.
4. **Single-Process Bureau Runner**: Provided `run_bureau.py` for local convenience, while preserving independent startup capability (`python agents/concierge.py`).

---

## 8. Known Issues and Failing Tests
- **Failing Tests**: **ZERO** (14 of 14 unit tests passing).
- **Proactive Notification**: ASI:One chat sessions cannot be initiated proactively by the agent if the user closes the window. Escalation updates are delivered reliably through the `/status` command, which renders the live chronological audit trail card.

---

## 9. Demo State
- **`DEMO_MODE`**: `1` (accelerates deadlines and redirects emails safely).
- **Deadlines in Seconds**:
  - Live intake flow: `120s` (2 minutes).
  - Quick test seeder (`scripts/seed_demo_case.py`): `30s`.
- **Seeded Demo Case ID**: `REC-DEMO2026`
- **Exact Demo Prompt**:
  > *"Flipkart delivered a broken Samsung Galaxy phone worth ₹24,999 and refused my refund."*

---

## 10. Invariants (DO NOT CHANGE)
1. **Agent Chat Protocol (ACP)** must remain the primary interface for all agents.
2. **`card_protocol_version: "1"`** and `requires_card_interaction: "true"` are mandatory in all card metadata.
3. **DEMO_MODE safety**: Never email real company addresses in demo mode. Always respect `DEMO_RECIPIENT_OVERRIDE`.
4. **Free Tier**: Intake, research, drafting, and initial dispatch must NEVER be blocked by the Payment Protocol.

---

## 11. Next 3 Actions
1. **Set `DEMO_RECIPIENT_OVERRIDE` and optional `RESEND_API_KEY` in `.env`** to receive real emails.
2. **Start the Bureau runner** (`python run_bureau.py`) on a persistent terminal.
3. **Open ASI:One, run the live demo prompt, and generate the Public Shared Chat URL**.

---

## 12. Resume Instructions for a Fresh Session
1. Read this file (`anchor.md`) completely.
2. Run `TESTING=1 PYTHONPATH=. .venv/bin/pytest tests/` to confirm all 14 tests pass.
3. Verify that all 5 agents are active on Agentverse (`python -c "import asyncio, aiohttp; ..."`).
4. Launch the agents: `python run_bureau.py`.
