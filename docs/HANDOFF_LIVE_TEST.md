# ReclaimAI — Live Test & Handoff Brief (post-fix)

> Prepared 2026-10-24 ~13:45 IST after the chat reliability fix session.
> Submission closes **17:50 IST today**. For the next tester (final polish
> owner). Rules live in `AGENTS.md`; state lives in `anchor.md`.

## 1. What happened today (30-second history)

- Live ASI:One chat was broken: welcome arrived, every real message was
  silently swallowed, "AI is working…" spun forever.
- Root causes (all reproduced offline, all fixed):
  1. `agents/concierge.py` missing `import re` — every TextContent died
     (`NameError`) right after the greeting.
  2. `save_case()` called with a nonexistent signature — intake never
     persisted.
  3. Rebuttal `DispatchRequest(tier=…)` used a field the model doesn't have.
  4. Sync OpenAI/Resend calls with no timeout inside the shared Bureau
     loop — 60s all-agent freezes.
- Fix register: `docs/TICKETS.md` (T1–T10). Commits `b5740a9..e080793`
  plus `2030a88`. 7 new regression tests; suite gate is **22 passed**:
  `TESTING=1 PYTHONPATH=. .venv/bin/pytest tests/ -q`.

## 2. Verified LIVE today (user-run, ASI:One chat "Ping Reclaim AI")

13:34–13:41 IST, all on fixed code:
- `/ping`, `/cardtest` responded instantly; typed `1`/`2` fallbacks work.
- First-message complaint processed in full: greeting + analysis text +
  **Grievance Intake Confirmation** card (#REC-968D106F), LLM-extracted
  company/amount/order ref.
- Card clicks verified the whole chain: Intake → **Legal Rights card**
  (Rule 4(4)/4(5) CP Act citations; grievance.officer@flipkart.com;
  NCH/e-Daakhil next tier) → **Notice Review card** (real ASI:One-drafted
  statutory notice) → **Approve & Send** → **Dispatched & Tracking card**.
- Real Resend delivery landed in the DEMO override inbox with the
  `[DEMO_MODE ACTIVE: Original Recipient=…]` banner — DEMO safety proven.
- Payment protocol rendered in-chat: `RequestPayment` FET 0.001 card,
  insufficient-balance note, Reject option.

## 3. Remaining live checks (in order)

1. `/status` — timeline carousel; watch the ~2-min Watcher escalation
   (`AUTONOMOUS_ESCALATION_TRIGGERED`, `ESCALATION_EMAIL_SENT`).
2. `/reply Flipkart: full refund initiated` → RESOLVED card.
3. `/reply Flipkart: return rejected, doorstep signed` → rebuttal card
   (exercises the T2 fix live).
4. `/edaakhil` → petition packet card. `/health` → honest config card.
5. On-chain payment demo: `scripts/run_buyer_agent.py` — or fund the
   concierge fee wallet on Dorado testnet for the in-chat card flow.
6. Housekeeping: purge stale `TEST-%` cases from `cases.db`; keep
   `DEMO_RECIPIENT_OVERRIDE` set while `RESEND_API_KEY` is on.
7. Submission assets: Share Chat URL from ASI:One, demo video per
   `docs/demo_script.md`, dashboard submission before 17:50 IST.

## 4. Hard rules for the polish owner (from AGENTS.md — binding)

- Never change seeds/addresses (breaks Agentverse registration).
- Never commit `.env*`, `cases.db`, `logs/`, key material.
- Python 3.11 venv only (`python3.11 -m venv .venv`); deps pinned in
  `requirements.txt` (no upgrades without research + approval).
- New citations must be verified against `anchor.md` §5 before commit.
- Commit format `<type>(<scope>): what changed`; one logical change per
  commit. Push only on the project owner's word.
- DEMO_MODE email redirect must never be weakened; payment verification
  stays strictly on-chain via cosmpy.

## 5. Quick commands

```bash
TESTING=1 PYTHONPATH=. .venv/bin/pytest tests/ -q   # 22 passed = gate
pkill -f run_bureau.py; .venv/bin/python run_bureau.py
tail -f logs/live.log
.venv/bin/python scripts/seed_demo_case.py         # 30s escalation demo
.venv/bin/python scripts/failure_drill.py          # resilience drill
.venv/bin/python scripts/run_buyer_agent.py        # FET payment round-trip
```
