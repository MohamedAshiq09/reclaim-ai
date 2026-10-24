---
name: git-commit-hygiene
description: Atomic commit sizing, conventional message format, staging discipline, push policy and anchor.md follow-up commits for ReclaimAI. Use for every commit in this repo.
---

# Git commit hygiene

## Approval gates

Two gates, both mandatory, in this order:

1. `code-review-agent` has returned an explicit `approved` verdict for
   the diff being committed.
2. The user has explicitly instructed commits for this change in this
   session. The user gates every commit; no agent commits autonomously.

If either gate is missing, ask for review or the user's go-ahead; do not
commit.

## Commit sizing

Commit as soon as a small, complete change is approved. Test: describe
the change in one sentence without "and". If you need "and", split it.

## Messages

Format: `<type>(<scope>): <what changed>` or `<type>: <what changed>`.

Allowed types: `feat`, `fix`, `docs`, `test`, `chore`, `refactor`.
Allowed scopes: `agent`, `cards`, `payment`, `common`, `scripts`,
`legal`, `tests`, `agentverse`, `workflow`.

Specific, never generic. Examples: `feat(cards): add case strength card`,
`fix(payment): reject duplicate transaction_id`,
`test(common): cover reply classifier fallback`. Reject `wip`, `updates`,
`fix stuff`.

## Staging

Run `git status` and inspect the diff first. Stage only files relevant to
the change. Never stage `.env*`, `cases.db`, seeds, key material,
`logs/`, `.venv/`, `__pycache__/` or `.pytest_cache/`. Never stage a
teammate's uncommitted deletions or renames without explicit user
instruction naming them (current case: the pending removal of the
duplicate `.claude/`, `.agents/`, `.cursor/` skill copies).

## Push policy

Commit locally on user instruction only. Do not push unless the user
explicitly asks. Never force-push or rewrite published history without
an explicit request.

## anchor.md follow-up

After the code commit, the builder updates `anchor.md` with the outcome,
commit hash and proof paths. Commit that state change separately as
`docs(anchor): record <task>` — again on user instruction. Verify the
entry against command output before committing it.

## Finish

Leave `git status --short` clean or declare every remaining item in
`anchor.md` with its purpose.
