---
name: python-venv-package
description: Authoritative project setup for Fetch.ai uAgent codebases that use the standard library `venv` plus `pip` and `requirements.txt`. Owns virtualenv creation, dependency installation, freezing, and run commands. Use when the project has a `requirements.txt` or a top-level `.venv/` directory, or when the user explicitly chose `Python venv package` in `fetch-skills`. Other skills (chat-protocol, stripe-payment-protocol, fet-payment-protocol) defer to this skill for setup commands when it is installed.
---

# Python venv + pip Setup (Fetch.ai uAgents)

## Purpose

Single source of truth for environment setup in uAgent projects that use the standard library `venv` module plus `pip` and `requirements.txt`. Whenever a protocol skill needs to install a dependency, run the agent, regenerate `requirements.txt`, or activate the virtualenv, defer to this skill.

## When to Use

- The project root contains `requirements.txt`, `requirements-dev.txt`, or a `.venv/` directory.
- The user selected `Python venv package` in the `fetch-skills` installer.
- A constrained environment without `uv` or Poetry available (CI sandboxes, locked machines).

## When NOT to Use

- The project uses `uv` (`uv.lock` or `[tool.uv]`) — use `uv-package`.
- The project uses Poetry (`poetry.lock` or `[tool.poetry]`) — use `poetry-package`.
- The user wants code only without a package setup — use `no-package`.

---

## Required Tooling

Python 3.11 or newer with the `venv` module (default in CPython). Verify:

```bash
python3.11 --version
```

If `python3.11` is not on PATH, fall back to `python3` and pin the version with `requires-python` later via `pyproject.toml` only if the project actually needs `pyproject.toml`. For a pure `requirements.txt` project, no `pyproject.toml` is required.

---

## Bootstrap a New Project

```bash
mkdir agent
cd agent
python3.11 -m venv .venv
source .venv/bin/activate           # macOS / Linux
# .venv\Scripts\Activate.ps1        # Windows PowerShell
python -m pip install --upgrade pip
pip install uagents uagents-core python-dotenv
pip freeze > requirements.txt
```

After this:

- `.venv/` is the virtualenv (must be gitignored).
- `requirements.txt` records the installed versions (must be committed).

---

## Add Dependencies

Activate the venv first if it is not already active:

```bash
source .venv/bin/activate
```

| Need | Command |
| --- | --- |
| Base uAgent deps | `pip install uagents uagents-core python-dotenv` |
| Stripe payment protocol | `pip install stripe` |
| FET payment protocol | `pip install cosmpy` |
| OpenAI client | `pip install openai` |
| Anthropic client | `pip install anthropic` |
| HTTP client (preferred) | `pip install httpx` |
| Dev tools | `pip install pytest ruff` |

After every install, refresh the lockfile:

```bash
pip freeze > requirements.txt
```

For dev tooling, keep a separate file:

```bash
pip install pytest ruff
pip freeze > requirements-dev.txt
```

`requirements-dev.txt` should start with `-r requirements.txt` so it pins both runtime and dev deps consistently.

## Install From Lockfile

On a fresh checkout or in CI:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For dev:

```bash
pip install -r requirements-dev.txt
```

## Run the Agent

```bash
source .venv/bin/activate
python agent.py
```

For one-shot commands without activating:

```bash
.venv/bin/python agent.py
.venv/bin/pytest
```

---

## Generated Project Files

### `.env.example`

```dotenv
# Agent identity
AGENT_NAME=my-agent
AGENT_SEED=replace-with-a-strong-secret-seed
AGENT_PORT=8000
AGENT_ENDPOINT=
AGENT_MAILBOX=true
```

Append protocol-specific blocks (Stripe, FET) from the relevant protocol skill.

### `.gitignore`

```gitignore
# Python
__pycache__/
*.pyc
*.pyo
.Python

# Virtualenv
.venv/
venv/
env/

# Environment / secrets
.env
.env.*.local

# IDE / OS
.idea/
.vscode/
.DS_Store

# Test / coverage
.pytest_cache/
.coverage
htmlcov/
```

### `README.md` Quick Start

````markdown
## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# fill in AGENT_SEED and any protocol secrets
python agent.py
```
````

---

## Hard Rules

- Always create the venv with an explicit interpreter (`python3.11 -m venv .venv`); never trust unversioned `python`.
- Always activate the venv (or use `.venv/bin/python` / `.venv/bin/pip` directly) before running any command.
- Always run `pip freeze > requirements.txt` after `pip install` so the lockfile stays accurate.
- Always commit `requirements.txt`. Never commit `.venv/`.
- Never `pip install` into the system Python; this skill assumes a project-local `.venv/`.
- Never mix `pip` with `uv` or Poetry inside the same project.

## Composition With Protocol Skills

When a protocol skill needs a new dependency:

1. Activate the venv.
2. Use the table above to map protocol → package.
3. Run `pip install <pkg>` then `pip freeze > requirements.txt`.
4. Continue with the protocol skill's code generation.

This skill does not generate any agent code itself — it only owns environment setup commands.
