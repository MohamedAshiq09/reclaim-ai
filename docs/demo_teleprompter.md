# ReclaimAI — 3-Minute Video Teleprompter Script

> **Event**: Fetch-A-Thon 3.0 (Fetch.ai Innovation Lab)  
> **Challenge**: ASI:One Agent Challenge — From Intent to Action  
> **Target Video Length**: Exactly 3 minutes (0:00 to 3:00)  
> **Format**: Live Screen Recording + Spoken Voiceover  

---

## 🎬 Video Overview & Recommended Structure

For a **3-minute limit**, the winning format is a **tight hybrid flow**:
1. **0:00 – 0:25 (25s)**: **Problem & 5-Agent Architecture** — Show `docs/explainer.html` in browser.
2. **0:25 – 1:40 (75s)**: **Live ASI:One Chat Execution** — Prompt → Intake Card → Rights Card → Notice Review Card → Dispatch.
3. **1:40 – 2:05 (25s)**: **Proof of Delivery** — Switch to Gmail tab to show the real dispatched legal notice.
4. **2:05 – 2:40 (35s)**: **On-Chain FET Payment & Autonomous Escalation** — Terminal running Buyer Agent + Watcher surveillance.
5. **2:40 – 3:00 (20s)**: **Closing & Architecture Summary** — Return to Agentverse / explainer dashboard.

---

## ⏱️ Second-by-Second Teleprompter Script

---

### [0:00 – 0:25] ACT 1: The Problem & Architecture (25 Seconds)

**🖥️ On-Screen Display:**  
- Fullscreen browser showing `docs/explainer.html` (open `file:///home/ash09/personal-projects/reclaim-ai/docs/explainer.html`).
- Hover over the 5 Agent badges (*Concierge, Researcher, Drafter, Dispatcher, Watcher*).

**🎙️ Spoken Voiceover:**  
> *"Hello judges! Every year, Indian consumers lose thousands of crores to broken deliveries, airline cancellations, and delayed refunds. Consumers give up because they don’t know their statutory rights, don't know the official Grievance Officer, and can't spend weeks following up.*  
> *Meet **ReclaimAI** — a 5-agent Fetch.ai Bureau that turns consumer intent into legally binding, autonomous action directly inside ASI:One."*

---

### [0:25 – 0:50] ACT 2A: The Complaint & Intake Form Card (25 Seconds)

**🖥️ On-Screen Display:**  
- Switch tab to the **ASI:One chat interface** with `@reclaim-ai` agent.
- Paste and send the prompt:  
  `Flipkart delivered a broken Samsung Galaxy phone worth ₹24,999 and customer care is refusing a refund saying the outer box was fine. Complainant: Ashiq, ash@example.com, Bengaluru.`

**🎙️ Spoken Voiceover:**  
> *"Let's see it live. I submit a real-world grievance in plain English.  
> Immediately, our Concierge agent receives the message via the Agent Chat Protocol, extracts the key facts using the ASI:One LLM, and responds not with static text, but with an **ASI:One Interactive Form Card**."*

**🖱️ On-Screen Action:**  
- Show the card rendering. Point out the extracted fields (Entity: *Flipkart*, Amount: *₹24,999*, Category: *E-commerce*).
- Click the primary button: **[Verify & Research Rights]**.

---

### [0:50 – 1:15] ACT 2B: Statutory Research & Verified Citation (25 Seconds)

**🖥️ On-Screen Display:**  
- The Concierge queries the **Researcher Agent** in the background.
- The **ASI:One Interactive Detail Card** appears with verified Indian consumer protection law.

**🎙️ Spoken Voiceover:**  
> *"The Researcher agent analyzes Indian statutory law and retrieves verified facts:*  
> *Rule 4(4) and Rule 4(5) of the Consumer Protection E-Commerce Rules 2020 — mandating a Grievance Officer, a 48-hour acknowledgment, and a 30-day resolution window.*  
> *Notice it also pulled Flipkart's official Grievance portal URL. While I read these rights, our Concierge has already speculatively drafted the notice in the background!"*

**🖱️ On-Screen Action:**  
- Hover over the verified URL and citation points.
- Click the primary button: **[Draft Formal Grievance Notice]**.

---

### [1:15 – 1:40] ACT 2C: Notice Review & One-Click Dispatch (25 Seconds)

**🖥️ On-Screen Display:**  
- **Instant render (<0.1s)** of the **ASI:One Interactive Review Card**.
- Show the clean legal draft: today's date (`24 October 2026`), personalized complainant details, zero `[...]` placeholders.

**🎙️ Spoken Voiceover:**  
> *"Thanks to background pre-drafting, the Review Card appears instantly.  
> The Drafter agent has prepared a formal statutory grievance letter citing the Consumer Protection Act 2019, giving a strict 15-day deadline before CCPA and e-Daakhil filing.  
> It has today's live date, no placeholder brackets, and full legal gravitas. Let's send it."*

**🖱️ On-Screen Action:**  
- Scroll slightly to show the letter structure.
- Click: **[Approve & Send Notice]**.
- Confirmation message appears: *"Formal grievance notice dispatched via Resend API (Dispatch ID: 01a16...)"*.

---

### [1:40 – 2:05] ACT 3: Proof of Live Outbound Delivery (25 Seconds)

**🖥️ On-Screen Display:**  
- Switch tab to your **Gmail inbox** (`ash@example.com` / `DEMO_RECIPIENT_OVERRIDE`).
- Open the email that just arrived from `onboarding@resend.dev` / `ReclaimAI Dispatcher`.

**🎙️ Spoken Voiceover:**  
> *"In real time, our Dispatcher agent fired the notice via the Resend API.  
> Here in my inbox is the formal legal grievance notice, complete with statutory references, order amount, and formal notice of legal action.  
> This isn't a passive chatbot simulation — the email is delivered to the nodal grievance channel."*

---

### [2:05 – 2:40] ACT 4: On-Chain FET Payment & Autonomous Escalation (35 Seconds)

**🖥️ On-Screen Display:**  
- Switch back to ASI:One or split-screen with Terminal.
- Type `/status` in ASI:One to show the live chronological audit trail card.
- In terminal, show:
  ```bash
  .venv/bin/python scripts/demo_terminal_step.py
  ```
- This prints both the **cosmpy on-chain ledger verifier** and the **autonomous Watcher escalation event log** from `cases.db`.

**🎙️ Spoken Voiceover:**  
> *"Now for autonomous tracking. Through the official Fetch.ai Payment Protocol, the Concierge sells the Auto-Escalation Pack for 0.001 FET.  
> As our buyer agent demonstrates, the transaction is verified strictly on-chain on Fetch.ai testnet using `cosmpy`.  
> Once funded, our **Watcher Agent** runs an autonomous background interval. If the company fails to resolve the grievance before the statutory deadline, the Watcher automatically generates a Tier-2 escalation to the National Consumer Helpline and e-Daakhil!"*

---

### [2:40 – 3:00] ACT 5: Closing & Hackathon Criteria Recap (20 Seconds)

**🖥️ On-Screen Display:**  
- Switch back to `docs/explainer.html` or Agentverse Dashboard showing all 5 registered agents with active mailboxes.

**🎙️ Spoken Voiceover:**  
> *"To summarize: ReclaimAI is 100% compliant with the Fetch-A-Thon 3.0 challenge:  
> Five distinct uAgents with registered Agentverse mailboxes, full Agent Chat Protocol compliance, ASI:One Interactive Cards v1, on-chain FET payments, and autonomous action that protects Indian consumers.  
> Thank you!"*

---

## 📋 Quick Pre-Flight Recording Checklist

Before hitting Record, have these 3 tabs open:
1. **Tab 1**: `file:///home/ash09/personal-projects/reclaim-ai/docs/explainer.html` (The interactive architecture explainer).
2. **Tab 2**: **ASI:One Chat** with `@reclaim-ai`.
3. **Tab 3**: Your **Gmail inbox** (ready to show the incoming email).
4. **Terminal Window**: Split at bottom or ready on Alt+Tab with:
   ```bash
   .venv/bin/python scripts/run_buyer_agent.py
   ```

### 💡 Copy-Paste Prompt for Live Demo:
```text
Flipkart delivered a broken Samsung Galaxy phone worth ₹24,999 and customer care is refusing a refund saying the outer box was fine. Complainant: Ashiq, ash@example.com, Bengaluru.
```
