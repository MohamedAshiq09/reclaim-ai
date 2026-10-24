---
name: code-review-gate
description: Checklist for reviewing any ReclaimAI diff before commit. Use when code-review-agent reviews a builder change, or when a builder self-checks before requesting review.
---

# Code review gate

Read `AGENTS.md` section 2 and `anchor.md` before reviewing anything.

## Pass order

1. **Ownership.** Does every changed file live in the requesting
   builder's paths (AGENTS.md section 4)? Cross-seam edits are rejected.
2. **Scope.** One logical change? Unrelated work is split before deep
   review.
3. **Non-negotiables.**
   - Dynamic, high-quality code; no placeholder or fake-success paths.
   - No new mock paths beyond the sanctioned fallbacks declared in
     `anchor.md` section 6 (curated contact table, simulated dispatch
     without `RESEND_API_KEY`), both env-gated and loudly logged.
   - Payment strictly on-chain via `fet_payments/ledger.py`; offline
     acceptance only with explicit `DEMO_PAYMENT_BYPASS=1` and loud
     warning logs; the free tier is never payment-gated.
   - No `.env*` changes, seeds, `cases.db` or key material touched or
     logged.
   - Synthetic ASI:One chat traffic: forbidden, unconditionally.
4. **Verification evidence.** The builder must show the command it ran
   and the observed result: `TESTING=1 PYTHONPATH=. .venv/bin/pytest
   tests/ -q`, plus agent import (`TESTING=1 ... -c "import agents.X"`)
   or script run, or the recorded live step from
   `docs/LIVE_TEST_CHECKLIST.md`.
5. **Tests.** Changed runtime behavior has a new or updated offline test
   and at least one relevant failure path. Docs/workflow-only changes
   still need path and command verification.
6. **Stack checks.**
   - `from __future__ import annotations` present; type hints on public
     functions; pydantic wire models only for inter-agent messages.
   - Cards: built through `common/cards.py`; `card_protocol_version: "1"`
     and `requires_card_interaction: "true"` unless terminal; payload
     matches the Predefined Card Schemas v1 shape.
   - LLM: deterministic fallback present and testable with no
     `ASI_ONE_API_KEY`; handlers never raise on malformed input.
   - DB: `sqlite3` only inside `common/db.py`; logging only via
     `common/logging.py` helpers.
   - Demo safety: `DEMO_RECIPIENT_OVERRIDE` path intact; no real company
     address reachable in demo mode.
7. **anchor.md.** Do hashes, paths and status claims match `git log` and
   command output? Is the Session State block accurate?
8. **Commit readiness.** A precise `<type>(<scope>): <what changed>`
   message is possible without "and".

## Verdict

Always return an explicit verdict:

```text
Scope: <result>
Rules: <result>
Verification: <command and observed result>
Tests: <result>
anchor.md: <result>
Verdict: approved | changes required
Required changes: <specific list, if any>
```

Reject, do not fix. Rejection goes back to the builder.
