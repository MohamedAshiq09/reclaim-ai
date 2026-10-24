# ReclaimAI — Autonomous Consumer Rights & Dispute Redressal

![tag:innovationlab](https://img.shields.io/badge/innovationlab-3D8BD3)
![tag:hackathon](https://img.shields.io/badge/hackathon-5F43F1)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Fetch.ai uAgents](https://img.shields.io/badge/Fetch.ai-uAgents_v0.26-purple.svg)](https://fetch.ai/)
[![ASI:One Compatible](https://img.shields.io/badge/ASI:One-Interactive_Cards-emerald.svg)](https://asi1.ai/)
[![Payment Protocol](https://img.shields.io/badge/Payment_Protocol-FET_On--Chain-orange.svg)](https://fetch.ai/)

> **Fetch-A-Thon 3.0** — *ASI:One Agent Challenge: From Intent to Action*  
> **Tagline**: Turning Indian consumer grievances into researched, cited, dispatched legal notices with autonomous escalation and on-chain tracking.

---

## 🎯 Executive Summary

| Attribute | Details |
| :--- | :--- |
| **Problem Solved** | Indian consumers lose tens of thousands of crores annually to damaged e-commerce shipments, unrefunded flight cancellations, and arbitrary bank/telecom deductions. Existing AI tools stop at drafting a generic email; consumers fail to pursue claims due to lack of legal awareness, inaccessible grievance officer contacts, and tedious follow-ups. |
| **Target Users** | Indian consumers facing unresolved refund rejections across E-Commerce (Flipkart, Amazon, Myntra), Airlines (IndiGo, Air India, SpiceJet), Banking & UPI (HDFC, SBI, ICICI), and Telecom (Airtel, Jio). |
| **Outcome Produced** | An end-to-end autonomous action pipeline inside **ASI:One**: statutory research under the Consumer Protection Act, 2019, verified grievance nodal contact retrieval, formal legal notice generation, automated dispatch via Resend, on-chain FET Payment Protocol monetization, and **autonomous interval-based Tier-2 escalation** to the National Consumer Helpline (NCH) and regulatory ombudsmen. |

---

## 🤖 Deployed Agents Reference Table

All five agents implement the **Agent Chat Protocol (ACP)** and are registered on **Agentverse** and discoverable in **ASI:One**:

| Agent Name | Role | Deterministic Address | Network |
| :--- | :--- | :--- | :--- |
| **ReclaimAI Concierge** | Primary ASI:One orchestrator, intent classifier, Interactive Card manager, Payment Protocol seller | `agent1q2a0f0a8zyw3229agt7saxtvenftxwe0gry6nv02dzd78rvye98tzty77e7` | Fetch.ai Testnet |
| **ReclaimAI Researcher** | Statutory rights retrieval (CPA 2019, E-Commerce Rules, DGCA, RBI) & verified Grievance Officer lookup | `agent1qgktn2gauj62w4uaynnapajvsexxjgxuq8ylj6ru2503p9hxt09h6tcgaum` | Fetch.ai Testnet |
| **ReclaimAI Drafter** | ASI:One LLM legal notice drafter citing statutory sections and CCPA / e-Daakhil warnings | `agent1q00z4x9d574zttujnjwkj7zz7u0elv4jw4exrrefvqegjnz0dntu5cj5js0` | Fetch.ai Testnet |
| **ReclaimAI Dispatcher** | Safe email delivery via Resend API with exponential backoff and demo override safety | `agent1qg9evq8equ7kkt2nw8fkg2wgujr6sy69ucpeflyr28539rnx8v7ng2wuu8l` | Fetch.ai Testnet |
| **ReclaimAI Watcher** | Autonomous interval tracker (`@on_interval`), deadline surveillance, and Tier-2 escalation | `agent1qgz54hf8dzdvqsuf3ja9vfvdl25d9umed0r6y6vhalwtl2s0vqkmw3l0a46` | Fetch.ai Testnet |

---

## 🏗️ Architecture & Message Flow

```
                      +-----------------------------+
                      |           ASI:One           |
                      |   (User Chat Conversation)  |
                      +--------------+--------------+
                                     |
                          Agent Chat Protocol (ACP)
                                     |
                                     v
                        +-------------------------+
                        |     CONCIERGE AGENT     |
                        |   (Interactive Cards)   |
                        +----+--------+---------+-+
                             |        |         |
              ResearchRequest|        |         |DraftRequest
                             v        |         v
             +---------------+--+     |     +---+---------------+
             | RESEARCHER AGENT |     |     |   DRAFTER AGENT   |
             | (Statutes & Nodal|     |     | (ASI:One LLM Legal|
             |     Contacts)    |     |     |      Notice)      |
             +------------------+     |     +-------------------+
                                      |
                       DispatchRequest|
                                      v
                        +-------------------------+
                        |    DISPATCHER AGENT     |
                        |   (Resend API / SMTP)   |
                        +------------+------------+
                                     |
                       Notice Served | Cases.db
                                     v
                        +-------------------------+
                        |      WATCHER AGENT      |
                        | (Autonomous Interval)   |
                        |   [Timeout -> Escalate] |
                        +-------------------------+
```

### The State Machine
```
[INTAKE] ──(Form Card)──> [RESEARCHING] ──(Detail Card)──> [DRAFT_REVIEW] ──(Review Card)──> [SENT] ──> [WAITING]
                                                                                                            │
                                                                           (Deadline Passed: Autonomous)   │
                                                                                                            v
                                                                                                      [ESCALATED] (Tier 2 NCH/Ombudsman)
```

---

## 🃏 ASI:One Interactive Cards Utilized

ReclaimAI demonstrates full-spectrum utilization of predefined ASI:One Interactive Card schemas:

1. **`form` Card (Intake)**: Automatically pre-fills entities extracted by the ASI:One LLM (company name, disputed amount, order ID) and captures complainant contact details.
2. **`detail` Card (Statutory Rights)**: Presents mandatory redressal timelines (48-hour acknowledgment, 30-day resolution under Rule 5(4)), citation links, and verified Grievance Officer nodal contacts.
3. **`review` Card (Legal Notice Approval)**: Displays key-value summary rows and statutory notice excerpt with primary **Approve & Send Notice** and **Cancel/Edit** CTAs.
4. **`carousel` Card (Dispute Audit Timeline)**: Triggered via the `/status` command, presenting a live multi-card chronological audit trail of all automated events from SQLite (`cases.db`).

---

## 💳 Payment Protocol Integration (Monetization)

ReclaimAI implements the official Fetch.ai `payment_protocol_spec` with `role="seller"`:
- **Free Tier**: Intake, statutory rights research, verified Grievance Officer lookup, formal notice drafting, and initial dispatch are 100% free.
- **Premium Enforcement Pack**: Users can opt in to the **Autonomous 24/7 Escalation & Tracking Pack** for `0.001 FET` on testnet.
- **Verification Engine**: The seller agent verifies the transaction against the Fetch.ai ledger using `cosmpy` before committing the case to priority regulatory enforcement.

---

## ⚡ Quick Start & Local Execution

### 1. Prerequisites
- Python 3.11+
- Git

### 2. Clone and Setup Environment
```bash
git clone https://github.com/MohamedAshiq09/reclaim-ai.git
cd reclaim-ai

# Create virtual environment
uv venv --python 3.11 .venv
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### 3. Configure Credentials
Copy `.env.example` to `.env` and provide your keys:
```bash
cp .env.example .env
```

Key environment variables:
```bash
AGENTVERSE_API_KEY=your_agentverse_key        # Agentverse mailbox registration
ASI_ONE_API_KEY=your_asi_one_key              # ASI:One LLM API key
RESEND_API_KEY=your_resend_api_key            # Resend email API key
DEMO_MODE=1                                   # Safe demo routing (accelerates deadlines to 2 mins)
DEMO_RECIPIENT_OVERRIDE=your_email@gmail.com  # Recipient for test notice emails
```

### 4. Run Test Suite
Validate all model schemas, card builders, retrieval logic, and state transitions:
```bash
TESTING=1 PYTHONPATH=. .venv/bin/pytest tests/
```

### 5. Launch the 5-Agent Bureau
Run all five agents concurrently in a single orchestrated Bureau process:
```bash
./scripts/run_all.sh
# or:
python run_bureau.py
```

### 6. Seed Instant Demo Case (Optional)
To test watcher escalation and live status immediately without manual intake:
```bash
python scripts/seed_demo_case.py
```

---

## 📚 Official Citations & Verified Statutory Sources

All legal rules implemented in ReclaimAI have been verified against official government gazettes:

- **Consumer Protection (E-Commerce) Rules, 2020 (Rule 5(4))**: [Ministry of Consumer Affairs](https://consumeraffairs.nic.in/acts-and-rules/consumer-protection/consumer-protection-e-commerce-rules-2020)
- **Consumer Protection Act, 2019 (Act 35 of 2019)**: [Department of Consumer Affairs](https://consumeraffairs.nic.in)
- **DGCA Civil Aviation Requirements (CAR Section 3, Series M, Part IV)**: [Directorate General of Civil Aviation](https://www.dgca.gov.in)
- **Reserve Bank Integrated Ombudsman Scheme, 2021**: [Reserve Bank of India](https://cms.rbi.org.in)
- **National Consumer Helpline (NCH)**: [consumerhelpline.gov.in](https://consumerhelpline.gov.in)
- **e-Daakhil Online Commission Filing**: [edaakhil.nic.in](https://edaakhil.nic.in)

Detailed citations and verification dates are tracked in [docs/verified_facts.md](docs/verified_facts.md).

---

## 🏆 Hackathon Checklist & Deliverables

- [x] At least one agent registered on Agentverse (all 5 registered)
- [x] Implements Agent Chat Protocol (ACP)
- [x] Discoverable and directly usable inside ASI:One
- [x] Multi-agent orchestration across 5 distinct uAgents
- [x] Complete primary workflow executes inside ASI:One without custom frontend
- [x] ASI:One Interactive Cards (`form`, `detail`, `review`, `carousel`)
- [x] Native Fetch.ai Payment Protocol (`Funds`, `RequestPayment`, `CommitPayment`, `CompletePayment`)
- [x] Real-world problem solving with statutory citations
- [x] Public GitHub repository with documentation and Innovation Lab badges
