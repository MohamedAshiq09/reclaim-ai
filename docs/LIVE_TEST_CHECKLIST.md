# ReclaimAI Live Verification & Testing Checklist

This checklist provides step-by-step procedures to test ReclaimAI live in **ASI:One** and **Agentverse**, with expected outputs, terminal verification steps, and a results log.

---

## Prerequisites (Terminal 1)

1. Ensure the Multi-Agent Bureau is running locally in your terminal:
   ```bash
   .venv/bin/python run_bureau.py
   ```
2. In a second terminal, monitor the real-time live log:
   ```bash
   tail -f logs/live.log
   ```

---

## Test Suite Walkthrough

### Phase 1: Direct ASI:One Chat & Intake Flow

| Step | Action | Input Text in ASI:One | Expected Output | Verified? |
| :--- | :--- | :--- | :--- | :--- |
| **1.1** | Mention `@reclaim-ai` or select from dropdown | `@reclaim-ai Flipkart delivered a broken Samsung Galaxy phone worth ₹24,999 and refused my refund.` | Concierge acknowledges and renders **Case Intake Form Card** confirming Order ID, Amount, Defect. | [ ] |
| **1.2** | Confirm details | `Confirm details and proceed to legal research` *(or click Submit CTA)* | Concierge queries Researcher; renders **Statutory Rights Card** citing E-Commerce Rules 2020 Rule 4(4) & 4(5) and CPA 2019 Section 2(11). | [ ] |
| **1.3** | Review draft notice | `Generate formal legal notice` *(or click Review CTA)* | Concierge queries Drafter; renders **Notice Review Card** with complete statutory notice to `grievance.officer@flipkart.com` and **[Approve & Dispatch]** CTA. | [ ] |
| **1.4** | Approve dispatch | `Approve and dispatch notice` *(or click Approve CTA)* | Concierge instructs Dispatcher to send email, arms Watcher 48h timer, and renders **Notice Dispatched & Tracking Active Detail Card** with `[View Case Timeline]`. | [ ] |

---

### Phase 2: Reply-Aware Decision Loop (The Adaptive Agent)

Test how ReclaimAI's ASI:One LLM brain dynamically reacts to company responses instead of acting like a rigid pipeline:

| Scenario | Input in ASI:One Chat | Expected Agent Action | Verified? |
| :--- | :--- | :--- | :--- |
| **2.1: Rejection** | `/reply Flipkart customer care: "Return rejected as delivery checklist was signed by customer at doorstep."` | Agent classifies as **REJECTED**, cites statutory invalidity of unverified doorstep sign-off under CPA Section 2(47), and issues **Statutory Rebuttal Notice** with CCPA penalty warning. | [ ] |
| **2.2: Stalling** | `/reply Flipkart: "We have forwarded your concern to the logistics team. Please wait 15 business days for an update."` | Agent classifies as **STALLING**, notes that Rule 4(5) requires final redressal within 30 days, and issues a **Strict 24-Hour Ultimatum Warning**. | [ ] |
| **2.3: Resolution** | `/reply Flipkart: "We apologize for the inconvenience. A full refund of ₹24,999 has been initiated to your bank account."` | Agent classifies as **RESOLVED**, updates case status to `RESOLVED`, disarms the Watcher timer, and renders **Case Redressed Celebration Card**. | [ ] |

---

### Phase 3: Autonomous Watcher Escalation Drill

Demonstrate autonomous escalation when the enterprise ignores the statutory notice:

1. In your terminal, run the accelerated demo seeder:
   ```bash
   .venv/bin/python scripts/seed_demo_case.py
   ```
2. Wait 30 seconds for the statutory timer to expire without corporate resolution.
3. In terminal, observe the Watcher log:
   ```
   [watcher] Case #REC-DEMO2026 deadline passed with no company resolution. Triggering AUTONOMOUS ESCALATION!
   [outbound] DispatchRequest -> reclaimai_dispatcher tier=2
   ```
4. In ASI:One chat with `@reclaim-ai`, send:
   `/status`
5. **Expected Output**: Concierge returns the live audit trail card showing Tier-2 escalation to the **National Consumer Helpline (NCH)** and preparation of the **e-Daakhil Consumer Commission petition**.

---

### Phase 4: System Health & Failure Resilience

1. In ASI:One chat, send:
   `/health`
2. **Expected Output**: An interactive Health Card verifying all 5 agents, SQLite DB, Resend API, and ASI:One LLM connectivity.
3. Run the automated failure drill in terminal:
   ```bash
   .venv/bin/python scripts/failure_drill.py
   ```
4. **Expected Output**: Verifies that when search or external APIs fail, the agents fall back gracefully to verified statutory tables without crashing.

---

### Phase 5: Agent-to-Agent On-Chain Payment

Demonstrate multi-agent on-chain settlement on Fetch.ai testnet:

1. In terminal, run the autonomous Buyer agent:
   ```bash
   .venv/bin/python scripts/run_buyer_agent.py
   ```
2. **Expected Output**:
   - Buyer requests Priority Escalation Pack.
   - Concierge issues `RequestPayment(0.001 FET)`.
   - Buyer executes testnet transfer via `cosmpy`.
   - Buyer submits `CommitPayment(tx_hash)`.
   - Concierge verifies on testnet ledger and replies with `CompletePayment`.
   - Priority tracking is unlocked for the case!

---

## Live Results Audit Log

| Date & Time (IST) | Test Phase | Case ID | Result / Observation |
| :--- | :--- | :--- | :--- |
| 2026-10-24 11:31 | Phase 1 (Intake & Dispatch) | `#REC-4938165A` | **SUCCESS**: Rendered Notice Dispatched Detail Card live in ASI:One with active watcher. |
| 2026-10-24 | Phase 2 (Decision Loop) | | |
| 2026-10-24 | Phase 3 (Watcher Escalation) | | |
| 2026-10-24 | Phase 4 (Health & Resilience) | | |
| 2026-10-24 | Phase 5 (Buyer Payment) | | |
