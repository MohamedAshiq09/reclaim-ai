# ReclaimAI — Video & Live Demo Script (3 to 5 Minutes)

**Hackathon**: Fetch-A-Thon 3.0 (Fetch.ai Innovation Lab)  
**Challenge**: ASI:One Agent Challenge — From Intent to Action  
**System**: ReclaimAI — Autonomous Consumer Rights & Grievance Redressal (India)

---

## ⏱️ Timeline & Stage Directions

### [0:00 – 0:35] 1. The Real-World Problem: "The Indian Consumer Gap"
- **Visual**: Show a Flipkart/Airline refund rejection screenshot or state the statistic.
- **Narrative**:
  > *"Every year, Indian consumers lose thousands of crores to damaged deliveries, arbitrary flight cancellations, and unfair bank charges. Most people give up because they don’t know who the statutory Grievance Officer is, don't know the law, and don't have time to follow up.*
  > *Most AI assistants only draft a passive letter and leave the consumer stranded. ReclaimAI is fundamentally different: it turns intent into executable action across a 5-agent Fetch.ai team."*

---

### [0:35 – 1:20] 2. Discovery & Intake in ASI:One (Interactive Form Card)
- **Visual**: ASI:One conversation interface (no custom UI).
- **User Prompt**:
  > *"Flipkart delivered a broken Samsung Galaxy phone worth ₹24,999 and customer care is refusing a refund saying the outer box was fine."*
- **Agent Action**:
  - Concierge Agent receives the query via ACP (`ChatMessage`).
  - ASI:One LLM classifies the dispute category (`ecommerce`), extracts entity (`Flipkart`), order amount (`₹24,999`), and complaint summary.
  - Concierge returns an **ASI:One Interactive Form Card** pre-filled with the extracted facts.
- **Demo Step**: Show the interactive drawer opening inside ASI:One. Click **"Verify & Research Rights"**.

---

### [1:20 – 2:05] 3. Autonomous Rights Research (Interactive Detail Card)
- **Agent Action**:
  - Concierge invokes the **Researcher Agent** via `ResearchRequest`.
  - Researcher analyzes statutory rules (Rule 4(4) & Rule 4(5) of the Consumer Protection (E-Commerce) Rules, 2020) and retrieves the official Grievance Officer nodal contact (`grievance.officer@flipkart.com`).
  - Concierge presents an **ASI:One Interactive Detail Card** displaying:
    - Mandatory 48-hour acknowledgment rule (Rule 4(5)).
    - 30-day statutory resolution window (Rule 4(5)).
    - Verified Grievance Officer email and citation sources (Rule 4(4)).
- **Demo Step**: Point out the official citations and click **"Draft Formal Grievance Notice"**.

---

### [2:05 – 2:50] 4. Legal Notice Drafting & Review (Interactive Review Card)
- **Agent Action**:
  - Drafter Agent uses ASI:One LLM to generate a formal statutory grievance letter citing the Consumer Protection Act, 2019, Rule 4(4) & Rule 4(5), and warning of CCPA / e-Daakhil escalation.
  - Concierge presents an **ASI:One Interactive Review Card** with key-value summary rows and body preview.
- **Demo Step**: Click **"Approve & Send Notice"**.


---

### [2:50 – 3:35] 5. Action Moment: Live Dispatch (Dispatcher Agent)
- **Agent Action**:
  - Dispatcher Agent immediately transmits the notice via Resend API (routed to the demo inbox in DEMO_MODE so real companies aren't spammed).
  - Show the email landing in the inbox in real time, with the CC to the consumer.
  - Concierge returns confirmation with message ID and places the dispute under autonomous tracking.

---

### [3:35 – 4:15] 6. Autonomous Escalation & Payment Protocol
- **Agent Action**:
  - Concierge presents the **Fetch.ai Payment Protocol** offer for the "Auto-Escalation & Tracking Pack" (0.001 FET on testnet).
  - Demonstrate `RequestPayment` and `CommitPayment` verified on-chain by `cosmpy`.
  - **The Climax**: The statutory timer (accelerated to ~2 minutes in demo mode) expires without company resolution.
  - **Escalation Watcher Agent** autonomously wakes up on `@agent.on_interval`, formulates a **Tier-2 Regulatory Escalation** to the National Consumer Helpline (NCH) and e-Daakhil, and dispatches it without user intervention!
  - User types `/status`: An **ASI:One Interactive Carousel Card** opens, displaying the entire live timeline of autonomous actions.

---

### [4:15 – 4:45] 7. Technical Architecture & Reliability Drill
- **Visual**: Show terminal logs with structured `[inbound]`, `[outbound]`, `[payment]`, and `[state]` tags.
- **Narrative**:
  > *"ReclaimAI is built on 5 distinct uAgents: Concierge, Researcher, Drafter, Dispatcher, and Watcher. It implements the official Agent Chat Protocol (ACP), Agentverse manifest registration, native FET Payment Protocol, and ASI:One Interactive Cards at every milestone. It operates with SQLite transactional guarantees, retry backoffs, and safe demo redirection."*

---

### [4:45 – 5:00] 8. Summary & Post-Hackathon Viability
- **Conclusion**:
  > *"ReclaimAI doesn't just chat. It researches, cites, sends, tracks, and escalates. It is the future of autonomous consumer advocacy in the agentic economy."*
