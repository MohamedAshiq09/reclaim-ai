---
name: no-package
description: Code-only mode for Fetch.ai uAgent projects with no Python package manager attached. Use when the user explicitly chose `No package manager / code only` in `fetch-skills`, or when a snippet/sample is being added to an existing project that already manages dependencies elsewhere. Suppresses install / lockfile / virtualenv commands and only documents required runtime dependencies. Other skills (chat-protocol, stripe-payment-protocol, fet-payment-protocol) defer to this skill when no `uv-package`, `poetry-package`, or `python-venv-package` skill is installed.
---

# No Package Manager (Code-Only Mode)

## Purpose

Some users only want generated agent code — no `pyproject.toml`, no `requirements.txt`, no `.venv/`, no `uv add` / `poetry add` / `pip install` commands. This skill keeps protocol skills consistent in that mode by documenting required runtime dependencies without running anything.

## When to Use

- The user selected `No package manager / code only` in the `fetch-skills` installer.
- Pasting a uAgent snippet into a host application that already has its own environment.
- Quickly prototyping in a notebook / playground.
- A constrained sandbox where install commands are not allowed.

## When NOT to Use

- A real project that ships and runs on its own: pick `uv-package`, `poetry-package`, or `python-venv-package` instead.
- Anything that needs a reproducible build, lockfile, CI pipeline, or container image.

---

## Operating Rules

1. Do not run install commands. Never call `pip install`, `uv add`, `poetry add`, `python -m venv`, or any equivalent.
2. Do not generate `pyproject.toml`, `requirements.txt`, `poetry.lock`, `uv.lock`, or activate scripts.
3. Document required runtime packages as a plain Markdown list at the top of generated agent files, in a `## Dependencies` README section, or in a top-of-file docstring.
4. Run commands assume the user already has a working interpreter with the listed dependencies importable. Use `python agent.py`.
5. Still always generate `.env.example` for any agent that reads env vars; secrets are a separate concern from package management.
6. Still always recommend `.gitignore` entries for `.env`, `__pycache__/`, and editor / OS noise.

## Required Runtime Dependencies (Reference)

These are the import names the generated agent code needs at runtime. Surface them to the user as documentation, not as install commands.

| Protocol skill | Required imports |
| --- | --- |
| `chat-protocol` (base) | `uagents`, `uagents-core`, `python-dotenv` |
| `stripe-payment-protocol` | adds `stripe` |
| `fet-payment-protocol` | adds `cosmpy` |

Sample documentation block to put in the generated README or docstring:

```markdown
## Dependencies

This agent expects the following packages to be importable in your existing environment:

- `uagents`
- `uagents-core`
- `python-dotenv`
- `stripe`   # only if the Stripe payment protocol is used
- `cosmpy`   # only if the FET payment protocol is used

Install commands are intentionally omitted. Add these to your existing dependency manager
(`uv`, Poetry, pip, conda, monorepo tooling, etc.) using whatever flow your project already uses.
```

## Generated Project Files

### `.env.example` (always)

```dotenv
# Agent identity
AGENT_NAME=my-agent
AGENT_SEED=replace-with-a-strong-secret-seed
AGENT_PORT=8000
AGENT_ENDPOINT=
AGENT_MAILBOX=true
```

Append protocol-specific blocks (Stripe, FET) from the relevant protocol skill.

### `.gitignore` (always)

```gitignore
# Python
__pycache__/
*.pyc

# Environment / secrets
.env
.env.*.local

# IDE / OS
.idea/
.vscode/
.DS_Store
```

No virtualenv or lockfile entries are needed in this mode.

### `README.md` Quick Start

````markdown
## Quick start

```bash
# Ensure your environment provides:
#   uagents, uagents-core, python-dotenv
#   plus stripe / cosmpy if the relevant payment skill is used
cp .env.example .env
# fill in AGENT_SEED and any protocol secrets
python agent.py
```
````

---

## Hard Rules

- Never emit install commands.
- Never create or modify `pyproject.toml`, `requirements*.txt`, `uv.lock`, `poetry.lock`.
- Never assume a package manager exists. The user opted out.
- Always still document which packages must be importable.
- Always still create `.env.example` and recommend `.gitignore` entries for secrets.
- Never claim the agent will run if a required package is missing — surface the import list clearly.

## Composition With Protocol Skills

When a protocol skill would normally call `uv add` / `poetry add` / `pip install`:

1. Skip the install step.
2. Add the package name(s) to the `## Dependencies` block in the generated README or docstring.
3. Continue with the protocol skill's code generation.

This skill does not generate any agent code itself — it only enforces code-only behavior across the rest of the workflow.
