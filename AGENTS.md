# AGENTS.md — ReclaimAI

This file is the routing and rules contract read by every coding agent at the
start of every session. `anchor.md` is the state contract: read `anchor.md`
first to learn "where are we", then this file to learn "how we work". If a
task does not clearly belong to one owner in section 4, stop and ask rather
than guessing.

## 0. The state contract — read at start, update before finishing

**`anchor.md` in the repo root is the single source of "where are we".**

1. Read `anchor.md` at session start and whenever context becomes unclear.
   Assume a fresh agent resumes from `anchor.md` alone.
2. Update the Session State block, the Deliverables Status Table, and
   `Next 3 Actions` before finishing any chunk of work. Clear "In progress"
   when done. Every update must be specific and verifiable: commit hash plus
   the 1-3 file paths that prove the claim.
3. Point, do not paste. `anchor.md` is an index, not an archive. Detail
   lives in git history and the cited files. Never paste code, logs, or long
   explanations.
4. Every status claim must come from command output observed in that
   session. If a command was not run, write `unverified` instead of implying
   success.
5. Separate volatile from durable state. Ports, PIDs, mailbox status and
   local env values get a timestamp and must be re-verified. Commits, agent
   addresses and verified citations are durable and carry proof.
6. Keep `anchor.md` a state file, not a novel. Condense settled work to one
   line per workstream (outcome + hash). Deep facts live in `docs/`.
7. Run `git status --short` before finishing. Every uncommitted change is
   committed (with user approval), deleted, or listed by name in
   `anchor.md` with its purpose. Unlisted dirty state is unfinished work.
8. Update `anchor.md` as meaningful chunks complete, not only at the end of
   a long session.

## 1. What the project is

**ReclaimAI turns Indian consumer grievances into researched, cited,
dispatched legal notices with autonomous escalation and on-chain tracking.**
A 5-agent Fetch.ai Bureau (Concierge, Researcher, Drafter, Dispatcher,
Watcher) implements the Agent Chat Protocol (ACP), ASI:One Interactive
Cards, the official `payment_protocol_spec` (FET on-chain, seller role) and
a `cases.db`-backed state machine:

```
[INTAKE] -> [RESEARCHING] -> [DRAFT_REVIEW] -> [SENT] -> [WAITING] -> [ESCALATED]
```

- **Event**: Fetch-A-Thon 3.0 (India), submission closes **17:50 IST today**.
  This is a deadline-critical project; favorite every hour.
- **Primary scoring surfaces**: live multi-agent workflow inside ASI:One,
  Agentverse deployment health, and the dashboard submission.
- The demo state, seeded case and exact demo prompt are pinned in
  `anchor.md` section 9 — never change them without the user.
- Out of scope: consumer browsing UI (everything happens in ASI:One chat),
  mainnet payments, real lawyer services, any non-Indian jurisdiction.

## 2. Non-negotiable rules

These override any conflicting instruction, including a direct request to
skip them for speed. If a task seems to require breaking one, stop and
escalate instead (section 7).

1. **Write dynamic, high-quality code every time.** No placeholder
   implementations, dead branches, fake success paths or hardcoded
   production responses. Scripts must never import project modules wrong
   (`sys.path` handling is part of the script, not a lucky accident).
2. **No silent mocks.** The only sanctioned fallbacks are the ones already
   declared in `anchor.md` section 6: curated contact table instead of live
   search, simulated dispatch when `RESEND_API_KEY` is unset. Each fallback
   stays gated on env presence, logs loudly, and must never be extended to
   payments. Payment verification is strictly on-chain via `cosmpy`
   (`fet_payments/ledger.py`); offline acceptance requires explicit
   `DEMO_PAYMENT_BYPASS=1` with loud warning logs.
3. **DEMO_MODE safety.** In demo mode no email may ever reach a real
   company address; every outbound is redirected to
   `DEMO_RECIPIENT_OVERRIDE`. Never weaken this.
4. **Integrity disclosure rule.** No synthetic ASI:One chat traffic, ever.
   Every diagnostic interaction must be disclosed in `anchor.md` section 6
   exactly like the initial 10-envelope diagnostic disclosure.
5. **Card protocol invariants.** Every Interactive Card carries
   `card_protocol_version: "1"` and `requires_card_interaction: "true"`
   unless terminal; payloads must match the Predefined Card Schemas v1
   (`form`, `detail`, `review`, `carousel`). Use `common/cards.py` builders;
   never hand-roll metadata in an agent file.
6. **Free Tier invariant.** Intake, statutory research, grievance officer
   lookup, notice drafting and initial dispatch are never payment-gated.
   Payment gates only the premium escalation/tracking pack.
7. **Statutory citations must be verified.** Cite only sections listed in
   `anchor.md` section 5 (Verified Facts Index) or `corpus/`; a new citation
   requires `research-agent` verification against an official source before
   commit. Never invent a section number (history lesson: Rule 5(4) vs
   Rule 4(4), DGCA Part II vs Part IV).
8. **Environment files are off-limits.** Never read, modify or commit any
   real `.env*` file, `cases.db` content, or seeds. `.env.example` may be
   updated with placeholders only. Never log key material — including agent
   seeds, which are wallet secrets.
9. **Seeds and addresses are durable.** Agent addresses derive
   deterministically from seeds in `common/config.py`. Changing a seed
   changes the address and breaks Agentverse registration, mailbox polling
   and inter-agent routing. Never touch without explicit user approval.
10. **Pinned toolchain.** Dependency versions stay as pinned in
    `requirements.txt`/`common/config.py` (`uagents==0.26.1`,
    `uagents-core==0.4.12`, `cosmpy==0.12.2`, `pydantic==2.14.1`, Python
    3.11). No upgrade, no new dependency without `research-agent` input and
    user approval.
11. **Never break this section to get unstuck.** Escalate per section 7.

## 3. Codebase structure

Verified paths:

```text
reclaim-ai/
├── AGENTS.md                     this contract
├── anchor.md                     state contract (single source of "where we are")
├── opencode.json                 opencode config (skills.paths registration)
├── .opencode/agents/             6 subagent definitions (section 4)
├── .opencode/skills/             project skills (SKILL.md files)
├── agents/
│   ├── concierge.py              ASI:One orchestrator: chat proto + cards + payment seller
│   ├── researcher.py             statutory rights retrieval + grievance contact lookup
│   ├── drafter.py                ASI:One LLM legal notice drafting (tier 1 / tier 2)
│   ├── dispatcher.py             Resend email dispatch w/ demo override + backoff
│   └── watcher.py                @on_interval deadline surveillance + Tier-2 escalation
├── common/
│   ├── models.py                 pydantic/uAgents wire models (single message schema source)
│   ├── config.py                 env loading + seed/address configuration
│   ├── cards.py                  Interactive Card builders + parse_selection
│   ├── llm.py                    ASI:One client: intent, drafting, reply classification, packets
│   ├── db.py                     SQLite cases/events store
│   └── logging.py                live.log + ctx logger helpers
├── fet_payments/ledger.py        cosmpy on-chain FET verification (testnet)
├── corpus/                       digest of verified statutes (one file per domain)
├── scripts/                      register/seed/buyer demo tooling
├── tests/                        pytest suite (the repo's only automated gate)
├── docs/                         demo script, live test checklist, verified facts
├── run_bureau.py                 runs all 5 agents in one Bureau (port 8000)
└── requirements.txt              pinned deps (Python 3.11)
```

Working commands (verified on this machine; `uv` is NOT installed here):

```bash
# venv (one-time): python3.11 must be on PATH — it is at ~/.local/bin/python3.11
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt

# the repo's automated gate — REQUIRED before any review or commit
TESTING=1 PYTHONPATH=. .venv/bin/pytest tests/ -q

# run the full bureau
.venv/bin/python run_bureau.py

# follow the live audit log
tail -f logs/live.log

# demo tooling
.venv/bin/python scripts/seed_demo_case.py     # seeds REC-DEMO2026 (30s deadline)
.venv/bin/python scripts/run_buyer_agent.py    # payment round-trip demo (Phase 5)
```

- Port map (localhost fallback): concierge 8001, researcher 8002, drafter
  8003, dispatcher 8004, watcher 8005, bureau 8000.
- `TESTING=1` must be set for safe test runs; without it agent imports may
  attempt wallet funding and mailbox work.
- `TESTING=1` also guards `fund_agent_if_low` (see every agent file) —
  keep that guard when adding agents.

## 4. Subagent roster, routing and closing sequence

Two layers: three builders own code seams; three support agents are
cross-cutting and own no product code.

| Subagent | Owns | Depends on |
|---|---|---|
| `common-builder` | `common/**`, `fet_payments/**`, `tests/**`, `requirements.txt`, `.env.example` | `research-agent` for uAgents/cosmpy API facts |
| `pipeline-builder` | `agents/researcher.py`, `agents/drafter.py`, `agents/dispatcher.py`, `agents/watcher.py`, `run_bureau.py`, `scripts/**` | `common-builder`; `research-agent` |
| `concierge-builder` | `agents/concierge.py` | `common-builder`; `pipeline-builder`; `research-agent` |
| `research-agent` | `corpus/**`, `docs/verified_facts.md` (data updates only); no code | Invoked by any builder |
| `code-review-agent` | No code; reviews every diff and `anchor.md` update | Verified builder work |
| `git-commit-agent` | No code; atomic commits only | `code-review-agent` approval + user instruction |

Rules of engagement:

- No builder edits another builder's paths. If a change crosses a seam,
  hand the requirement to the owner rather than editing around them.
- New interactive cards, card payloads or `parse_selection` handling are
  `common-builder` + `concierge-builder` work only (builder + handler).
- Payment flow changes (seller or buyer side) always involve
  `concierge-builder`, and the on-chain verification path always goes
  through `common-builder`'s `fet_payments/ledger.py`.
- Wire models (`common/models.py`) change only via `common-builder`, as one
  commit that updates every consumer of the model.

Routing:

```text
common-builder -> pipeline-builder -> concierge-builder
                       |                  |  ^
                       +------------------+  |
        (concierge consumes pipeline's inter-agent messages)

any builder -> research-agent (factual/statutory lookup only)

builder -> code-review-agent -> git-commit-agent
        -> update anchor.md -> git-commit-agent (docs state commit)
```

Every builder task closes in this exact order:

1. **Implement** within owned paths.
2. **Verify by running it.** `TESTING=1 PYTHONPATH=. .venv/bin/pytest
   tests/ -q` green at minimum; for runtime features, exercise the
   relevant script/agent import or record the manual ASI:One step from
   `docs/LIVE_TEST_CHECKLIST.md` with timestamp in `anchor.md`.
3. **`code-review-agent`** reviews the code diff. No commit without an
   explicit approval verdict.
4. **`git-commit-agent`** makes atomic commits — only on the user's
   instruction (section 8).
5. **Update `anchor.md`** with the outcome, commit hash and proof paths.
6. **`git-commit-agent`** commits the state update as
   `docs(anchor): record <task>` on the user's instruction.

The `anchor.md` update is part of done, not an afterthought. A task with
code committed but a stale `anchor.md` is unfinished.

## 5. Coding standards

**General (all Python in this repo)**
- Python 3.11 syntax and stdlib; `from __future__ import annotations` at
  the top of every module, matching existing files.
- Type hints on all public functions. No `Any` leaking from
  `common/models.py` boundaries — pydantic models are the wire contract.
- Async handlers only async when they await; never block the bureau loop
  with `time.sleep` in a handler — use `asyncio.sleep` (see
  `agents/dispatcher.py:92` as the pattern).
- SQLite access is wrapped by `common/db.py` exclusively. No new
  `sqlite3.connect` calls anywhere else.
- All outbound logging goes through `common/logging.py` helpers so
  `logs/live.log` stays a single structured audit stream.
- Errors degrade gracefully (log + fallback + continue); a handler that
  raises on malformed input breaks the whole chat session.

**uAgents protocol layer (`agents/**`)**
- Every agent file follows the existing shape: seed from `common/config`,
  mailbox via `AGENTVERSE_API_KEY`, `TESTING` guard before
  `fund_agent_if_low`, `include(protocol)` at the bottom. Match it exactly
  for any new agent, and register it in `run_bureau.py` + `anchor.md`
  section 3 in the same task.
- Inter-agent messages use only `common/models.py` wire models with
  explicit `ctx.send(ADDRESS, msg)` and routing log via
  `log_outbound`. Never send plain dicts between agents.
- Every protocol change (model, action name, card handler) must be
  reflected in: the card payload builder, `parse_selection` heuristics,
  `docs/LIVE_TEST_CHECKLIST.md` when user-facing, and the pytest suite.

**ASI:One LLM layer (`common/llm.py`)**
- Live client via `api.asi1.ai/v1` with `ASI_ONE_API_KEY`; every function
  must have a deterministic heuristic fallback that keeps the agent alive
  when the key/API fails, and the fallback must be testable without
  network. Never let an LLM outage crash an agent.

**Payments (`fet_payments/`, `concierge`)**
- Follow `anchor.md` section 6: strict on-chain verification, explicit
  bypass env, idempotency on `transaction_id`, `RejectPayment` on failure.
- Amounts come from config (`FET_PAYMENT_AMOUNT`), never hardcoded.

**Testing (`tests/**`)**
- Pytest, offline, no network. Tests must target the heuristic/fallback
  paths (no `ASI_ONE_API_KEY` needed) and never create real mailboxes.
- Every new runtime behavior gets a test; every bug fix gets a
  regression test. A test that only exercises a happy path in isolation
  and the repo has no failure-path test for is incomplete.
- Keep `TESTING=1 CPF`-free: tests must pass with zero env config.

## 6. Definition of done

A task is done only when all of the following are true:

1. The change is inside the owning subagent's paths.
2. The pytest suite was run green this session for changed runtime
   behavior, and new/changed behavior has test coverage (docs-only
   changes must verify every referenced command and path instead).
3. Runtime verification was run and observed: agent imports with
   `TESTING=1`, script execution where relevant, or a recorded live
   ASI:One step from the checklist. `pytest` alone is not full
   verification of chat behavior.
4. `code-review-agent` approved the diff against section 2.
5. `git-commit-agent` created atomic commit(s) on the user's instruction,
   with the required message format.
6. `anchor.md` records the outcome, commit hash and proof paths, and the
   state update is committed (or declared if user has not approved
   committing).
7. `git status --short` is clean or every remaining item is declared in
   `anchor.md` (including `logs/live.log`, which is untracked by design).
8. No `.env*` file, `cases.db`, seed or key material changed.
9. No new mock path outside the sanctioned fallbacks in section 2.
10. Commands, dependencies or env contract changed? `README.md` "Quick
    Start", `.env.example` and `anchor.md` section 4 are updated in the
    same task.

## 7. Escalation protocol

- **Stuck twice on the same approach** -> invoke `research-agent` with the
  exact question, pinned version and the error text.
- **Still stuck after research, or the decision is scope/product/deadline
  trade-off** -> stop and ask the user directly. Do not pick a silent
  default.
- **Never work around a section 2 rule to get unstuck.** A workaround that
  violates a rule is a failed task, not a shortcut.
- **Never guess a uAgents/cosmpy/ASI:One API.** Use the skills (section 9),
  installed source, or `research-agent`.
- **Cross-seam change** -> ask the owning builder. Do not edit their files
  yourself.
- **Mailbox/Agentverse/live-traffic problems** -> hands-off to the user;
  agents never re-run registration scripts or synthetic senders on their
  own.

## 8. Git workflow

- **The user gates every commit.** Commit only on explicit user
  instruction ("commit", "commit this", the closing sequence with user
  go-ahead). No agent commits autonomously.
- Commit as soon as a small, complete change is approved by the user. Do
  not batch a session into one commit.
- Message format: `<type>(<scope>): what changed` or `<type>: what
  changed` — matching repo history (`feat(payment): ...`,
  `fix(legal): ...`, `docs: ...`).
  - types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`
  - scopes: `agent`, `cards`, `payment`, `common`, `scripts`, `legal`,
    `tests`, `agentverse`, `workflow`
- One logical change per commit. If the description needs "and", split it.
- Stage only the files relevant to the change. Inspect `git status` first.
  Never stage `.env*`, `cases.db`, `logs/`, `.venv/` or key material. Never
  stage another teammate's uncommitted deletions/renames (e.g. the pending
  removal of the duplicate `.claude/`, `.agents/`, `.cursor/` skill copies)
  without explicit user instruction.
- **Push policy:** agents may commit locally on instruction. Push only when
  the user explicitly asks. Never force-push or rewrite public history.
- The `anchor.md` state update is committed separately as
  `docs(anchor): record <task>` so code commit and state handoff stay
  atomic — or, if the user has not approved committing, the update is
  left uncommitted and declared in `git status` + `anchor.md`.

## 9. Workflow hygiene

### a. Skill registry

Never invoke a skill by a guessed name. Use this table. Project skills
live in `.opencode/skills/<name>/SKILL.md` (registered in `opencode.json`
under `skills.paths`, so they are discoverable as repo skills; restart
opencode after adding or changing skills). Historical note: the fetched
skills were consolidated from `.agent/.agents/.claude/.cursor/skills`
into `.opencode/skills` — those four directories are pending deletion in
git (section 8 cleanup decision).

| What you want | Exact skill name | Scope |
|---|---|---|
| Implement/extend ACP ChatMessage/Card/ack flows | `chat-protocol` | project |
| Implement the official payment protocol (multi-method) | `payment-protocol` | project |
| Add direct FET on-chain payments + cosmpy verifier | `fet-payment-protocol` | project |
| Add Stripe Checkout payments to an agent | `stripe-payment-protocol` | project |
| Set up venv + requirements.txt style projects | `python-venv-package` | project |
| Review a diff before commit | `code-review-gate` | project |
| Create atomic commits | `git-commit-hygiene` | project |
| Look up official docs/APIs without guessing | `research-source-protocol` | project |
| Bootstrap a tracking-free code-only project | `no-package` | project |
| Bootstrap a uv/pyproject project | `uv-package` | project (not used here) |
| Bootstrap a poetry project | `poetry-package` | project (not used here) |
| Debug a failure systematically | `systematic-debugging` | external |
| Diagnose a hard bug or performance regression | `diagnosing-bugs` | external |
| Verify a completion claim | `verification-before-completion` | external |
| Write tests first / red-green-refactor | `tdd` | external |
| Write an implementation plan | `writing-plans` | external |
| Execute a written plan | `executing-plans` | external |
| Change opencode config, agents or skills | `customize-opencode` | built-in |

`uv-package` and `poetry-package` are installed from earlier projects and
are NOT used by this repo (no `pyproject.toml`; dependency management is
`requirements.txt` + `.venv`). Do not run their setup commands unless the
user asks for them explicitly.

### b. No forward references

Never write "will do X" anywhere without either doing it now or filing it
under `Next 3 Actions` in `anchor.md`. Do not leave placeholder TODOs,
empty handlers or scripts referenced by docs but missing (current known
case: `docs/LIVE_TEST_CHECKLIST.md` Phase 4 references
`scripts/failure_drill.py`, which does not exist — owner:
`pipeline-builder`, logged in `anchor.md`).

### c. Session-end checklist

Run in this order and state the result:

1. `git status --short` — clean or declared. Every uncommitted change is
   committed (on user instruction), deleted, or listed by name in
   `anchor.md` with purpose.
2. `anchor.md` — Deliverables Status, Session State and `Next 3 Actions`
   reflect commands observed this session.
3. Pytest state — pass/fail count stated with the exact command used.
4. Background services — bureau processes, `tail -f`, Buyer agent and any
   other processes are left running or killed, and the state is stated in
   `anchor.md` with a timestamp.
5. Push status — pushed, or not pushed with the reason.
