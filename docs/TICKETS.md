# ReclaimAI — Ticket Register

> Raised 2026-10-24 ~13:20 IST from the live ASI:One chat bug report
> (1-min delayed welcome, complaint swallowed, "AI is working…" spinner
> forever, no direct answers). Full audit of `agents/**`, `common/**`
> performed prior to raising; every claim below cites file:line on HEAD
> `ef96423`.

## Severity strategy (deadline 17:50 IST)

- **T1–T4 (blockers)**: must land before any further live testing.
- **T5–T8 (experience)**: land before the 15:30 demo freeze; text-first.
- **T9–T10 (integrity/polish)**: land same session; small diffs.

---

## T1 — CRITICAL · Intake crash kills first complaint (BLOCKER)

- **Symptom**: user's actual complaint text is swallowed after the
  welcome — no intake card, spinner forever. Matches report exactly.
- **Root cause A** (primary): `handle_chat_message` stripped mention
  prefixes with `re.sub` but **never imported `re`** — every
  `TextContent` message raised `NameError: name 're' is not defined`
  right after the StartSession greeting was sent. Beneath the old
  code's exception silences this presented as: welcome arrives,
  complaint swallowed, spinner forever. Reproduced offline.
- **Root cause B** (again unfolded): `handle_initial_complaint_intent`
  called `save_case(user_address=..., facts=..., status=...)`
  (`agents/concierge.py:258-264`), but `common/db.py:50-61` defines
  `save_case(case_id, user_addr, category, company, facts_json, ...)`.
  → `TypeError: unexpected keyword argument` → handler dies → no
  outbound message (not even an error) → ASI:One spins forever.
- **Fix owner**: concierge-builder.
- **Fix**: add the missing `import re`; pass `category` +
  `facts_json=json.dumps(extracted)` with the correct kwarg names. Then
  crash-proof the call site (T7 pattern).
- **Verify**: new pytest flow test — first message containing
  `[StartSessionContent, TextContent(complaint)]` must produce ack +
  greeting + analysing text + review card, and persist the case to the
  (tmp-patched) DB.

## T2 — CRITICAL · Rebuttal path crashes on nonexistent model field (BLOCKER)

- **Symptom**: inbound company reply ("rejected"/"stalling") → silence.
- **Root cause**: `handle_send_rebuttal` builds
  `DispatchRequest(..., tier=1, ...)` (`agents/concierge.py:881-889`);
  `common/models.py:61-67` has **no** `tier` field on `DispatchRequest`
  → pydantic `ValidationError` at construction → handler dead.
- **Fix owner**: concierge-builder.
- **Fix**: drop the invalid kwarg (tier is carried via subject/case).
- **Verify**: pytest constructs the same DispatchRequest shape used by
  the handler without raising.

## T3 — CRITICAL · Sync LLM calls block the shared event loop (BLOCKER)

- **Symptom**: the ~60s hang before the welcome; all 5 agents stall
  together; "AI is working on your request…" spinner.
- **Root cause**: `common/llm.py` uses the **blocking** `OpenAI` client
  (`common/llm.py:6,13`) with **no timeout**, invoked directly inside
  async handlers: concierge `classify_intent_and_extract`
  (`concierge.py:247`), `classify_company_reply` (`concierge.py:790`),
  and drafter `generate_complaint_draft` (`drafter.py:64`).
  `run_bureau.py` runs all 5 agents in **one** asyncio loop → a single
  slow ASI:One call freezes the whole Bureau.
- **Fix owner**: common-builder + concierge-builder + pipeline-builder.
- **Fix**:
  1. `OpenAI(api_key, base_url, timeout=LLM_TIMEOUT_S, max_retries=1)`
     with `LLM_TIMEOUT_S` from env (default 20s, file
     `.env.example` entry added).
  2. Every agent call site offloads: `await asyncio.wait_for(
     asyncio.to_thread(fn, ...), N)` (concierge 12s classify, drafter
     30s draft, dispatcher 15s send).
  3. On `TimeoutError`: concierge falls back to the deterministic
     heuristic extraction; drafter to the deterministic template;
     dispatcher's existing retry/backoff handles the send.
- **Verify**: pytest with the client stripped — heuristic/deterministic
  paths still produce full responses offline.

## T4 — HIGH · Blocking Resend call inside async handler (BLOCKER)

- **Symptom**: 15–60s bureau-wide freeze at dispatch time.
- **Root cause**: `resend.Emails.send` (`agents/dispatcher.py:86`) is a
  blocking HTTP call inside an async fn; only the backoff sleeps are
  async. Note the irony: `asyncio.sleep` for retries, sync send in
  between.
- **Fix owner**: pipeline-builder.
- **Fix**: `await asyncio.wait_for(asyncio.to_thread(resend.Emails.send,
  params), 15)`; failures keep the existing `(False, None, err)` path.
- **Verify**: code review + existing flow untouched (`DispatchResult`
  contract unchanged).

## T5 — HIGH · No instant language; heavy work before first reply

- **Symptom**: spinner + late responses far over the declared ~3s
  first-touch budget from the live-test brief.
- **Root cause**: first message `[StartSessionContent, TextContent]` sends
  the greeting then (after T1 is fixed) immediately runs an LLM
  extraction before *any* narration; no cheap commands exist to test
  responsiveness from the chat itself.
- **Owner**: concierge-builder.
- **Fix**:
  1. On any complaint text: send an instant "analysing" narration text
     *before* the classify call.
  2. Add `/ping` (instant "pong + current step") and `/cardtest` (sends
     a review card immediately) to the command router
     (`concierge.py:189-203`).
  3. Narration-before-card is already correct in `card_message`
     (`common/cards.py:16-41` — TextContent precedes MetadataContent);
     keep that invariant.
- **Verify**: `/ping` handler unit test; live manual check.

## T6 — HIGH · Card-action parser misroutes prose; no text equivalents

- **Symptom**: button-driven flow works only when cards render; typed
  words like "approve"/"confirm" inside a *complaint* get treated as
  card clicks (e.g. "…refused to **confirm** my refund…" →
  `approve_dispatch` → bogus dispatch). No "1"/"yes"/"retry" fallbacks
  when card interaction is unavailable.
- **Root cause**: `parse_selection` prose rule
  (`common/cards.py:243-246`) matches action words anywhere in the text.
- **Owner**: common-builder (+ concierge state-aware mapping).
- **Fix**:
  1. Prose rule only for short whole-message commands (<= 48 chars) —
     complaint prose falls through to intent handling.
  2. Concierge: state-aware text equivalents for pending cards:
     `1|yes|ok|approve…` → the pending primary action;
     `2|no|edit|cancel…` → `reject_or_edit`; `retry` → re-run the last
     pending step (state table `FORM_PRESENTED → submit_case_facts`,
     `RESEARCH_COMPLETED → proceed_to_draft`, `DRAFT_REVIEW →
     approve_dispatch`, else `/status`).
- **Verify**: pytest — "I want to confirm my refund of the damaged
  product" parses to no action; "1" within `FORM_PRESENTED` state maps
  to `submit_case_facts`.

## T7 — HIGH · Silent handler deaths; no error resilience

- **Symptom**: any exception in `handle_chat_message` or a sub-handler
  ends the message with zero outbound text (the reported spinner).
- **Root cause**: no try/except around the content loop or sub-handlers
  (`concierge.py:155-228`); `log_error` exists (`common/logging.py:62`)
  but is unused in the concierge chat path.
- **Owner**: concierge-builder.
- **Fix**: wrap each content item; on failure `log_error` + one friendly
  text: "Something failed at step <X>. Reply **retry** to go again, or /
  status for a snapshot." Action handlers each get the same wrapper.
- **Verify**: pytest — forced exception inside intent handling still
  yields an outbound friendly text, process alive.

## T8 — MEDIUM · Citation drift vs Verified Facts Index

- **Symptom**: two citations disagree with `anchor.md` §5 (the verified
  facts index, each row with an official URL + verification date).
- **Findings**:
  - `agents/researcher.py:155-158` cites RB-IOS "**Section 8 & 11**" —
    §5 verifies **Clause 10 & 15** (30-day pre-escalation window; CMS
    escalation; compensation caps).
  - `agents/researcher.py:130` cites "Part II, **Para 3.3.2**" beyond
    the verified precision "**Para 3.3**".
- **Owner**: pipeline-builder W/ research-agent verification (aligning
  to already-verified facts; no new claims introduced).
- **Fix**: align researcher.py to §5 wording exactly.
- **Verify**: grep + file diff; §5 rows unchanged.

## T9 — MEDIUM · /health card presents hardcoded fictional telemetry

- **Symptom**: health reply asserts "ONLINE / 2ms" etc. for all
  components unconditionally (`concierge.py:945-955`) — a fake success
  path contradicting AGENTS.md rule 1/2 even when the Bureau is degraded.
- **Owner**: concierge-builder.
- **Fix**: derive status from real config/flags (`AGENTVERSE_API_KEY`,
  `ASI_ONE_API_KEY`, `RESEND_API_KEY`, `DEMO_MODE`, DB reachable via a
  `get_case` probe); drop fabricated latency numbers. Keep it a fast,
  honest read of *configuration health*.
- **Verify**: unit test asserts DEMO flag and API-key-derived rows.

## T10 — LOW · Workflow hygiene

- `docs/LIVE_TEST_CHECKLIST.md`: add Phase 0 quick checks (`/ping`,
  `/cardtest`, first-message full-flow) once T5 lands.
- `.env.example`: add `LLM_TIMEOUT_S` placeholder with comment.
- `anchor.md`: Session State, Deliverables, Next 3 Actions updated after
  each landed ticket.

---

## Explicitly NOT bugs (evidence on file)

- **DGCA "Para 3.3" / RBI "Clause 10 & 15"** flagged in the live-test
  brief: both are **VERIFIED** in `anchor.md` §5 with official source
  URLs (dgca.gov.in / cms.rbi.org.in) and decisions recorded §7.2–7.3.
  They stay. The only drift found is T8 above.
- **`card_message` narration ordering**: TextContent already precedes
  MetadataContent inside the same ChatMessage (`common/cards.py:34-41`)
  — the correct per-card-schema shape.
- **`Card` protocol invariants**: `requires_card_interaction` /
  `is_terminal` handling obey Predefined Card Schemas v1 everywhere
  checked (`common/cards.py:24-32`, all concierge call sites).
