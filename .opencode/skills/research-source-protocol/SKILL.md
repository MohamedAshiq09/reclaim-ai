---
name: research-source-protocol
description: How to look up official docs and APIs without guessing and report findings for ReclaimAI - Fetch.ai uAgents, ASI:One cards/protocols, cosmpy ledger, and Indian statutory sources. Use for every research-agent lookup and whenever a builder needs an installed-version API fact or a citation.
---

# Research source protocol

## Source order

1. Repo contract and state: `AGENTS.md`, `anchor.md` (especially section
   5 Verified Facts Index), `corpus/`, `docs/verified_facts.md`.
2. Installed package source in `.venv` for the pinned versions:
   `uagents` 0.26.1, `uagents-core` 0.4.12, `cosmpy` 0.12.2,
   `pydantic` 2.14.1. Read the actual installed code for exact behavior.
3. Official upstream docs for those versions: Fetch.ai Innovation Lab
   documentation, ASI:One Predefined Card Schemas v1, Agent Chat
   Protocol, `payment_protocol_spec`, Fetch.ai Ledger testnet.
4. Official Indian legal sources only for statutory facts:
   gazettes and portals on consumeraffairs.nic.in, dgca.gov.in,
   cms.rbi.org.in, consumerhelpline.gov.in, edaakhil.nic.in.
5. Community posts only as a last resort, clearly labeled unofficial.

## Report format

- Direct answer in one or two sentences.
- Official source URL and the exact version/section it applies to.
- Minimal applicable snippet or API signature; for statutes, the clause
  text and section number.
- What remains uncertain or version-dependent.
- Any conflict with the repo contract or verified facts.

## Rules

- Findings only. Never write, edit, stage or commit feature code.
- Never present a guess or an unofficial source as authoritative.
- Never assume an API from memory; check the installed version.
- For statutory facts, all four of: exact section, precise claim,
  official URL, verification date — before the fact enters `corpus/**`
  or `docs/verified_facts.md`. One missing item invalidates the record
  (history lesson: Rule 5(4) vs Rule 4(4) came from a sloppy citation).
- "Not found in official sources" is a complete, valid answer.
- Never include secrets, tokens or private keys in a report.
