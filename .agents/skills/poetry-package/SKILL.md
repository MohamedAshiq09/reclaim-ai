---
name: poetry-package
description: Authoritative project setup for Fetch.ai uAgent codebases that use Poetry as the Python package manager. Owns dependency installation, lockfile management, virtual environment creation, run commands, and `pyproject.toml` shape. Use when the project has a `poetry.lock` or `[tool.poetry]` block, or when the user explicitly chose `Poetry package` in `fetch-skills`. Other skills (chat-protocol, stripe-payment-protocol, fet-payment-protocol) defer to this skill for setup commands when it is installed.
---

# Poetry Package Setup (Fetch.ai uAgents)

## Purpose

Single source of truth for environment setup in uAgent projects that use Poetry. Whenever a protocol skill needs to install a dependency, run the agent, generate a lockfile, or create `pyproject.toml`, defer to this skill instead of inventing commands.

## When to Use

- The project root contains `poetry.lock` or `[tool.poetry]` in `pyproject.toml`.
- The user selected `Poetry package` in the `fetch-skills` installer.

## When NOT to Use

- The project uses `uv` (`uv.lock` or `[tool.uv]`) — use `uv-package`.
- The project uses plain venv + pip (`requirements.txt`, `.venv/`) — use `python-venv-package`.
- The user wants code only without a package setup — use `no-package`.

---

## Required Tooling

Poetry 1.8.x or newer. If missing, install once per machine:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Pin the project's interpreter explicitly so Poetry does not pick a system Python by accident:

```bash
poetry env use python3.11
```

---

## Bootstrap a New Project

```bash
poetry new --src agent
cd agent
poetry env use python3.11
poetry add uagents uagents-core python-dotenv
```

Recommended `pyproject.toml`:

```toml
[tool.poetry]
name = "agent"
version = "0.1.0"
description = "Fetch.ai uAgent"
authors = []
readme = "README.md"
package-mode = false

[tool.poetry.dependencies]
python = "^3.11"
uagents = "*"
uagents-core = "*"
python-dotenv = "*"

[tool.poetry.group.dev.dependencies]
pytest = "*"
ruff = "*"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

`package-mode = false` is correct for a runnable agent (not a library). Drop it if the project is meant to be packaged and published.

---

## Add Dependencies

| Need | Command |
| --- | --- |
| Base uAgent deps | `poetry add uagents uagents-core python-dotenv` |
| Stripe payment protocol | `poetry add stripe` |
| FET payment protocol | `poetry add cosmpy` |
| OpenAI client | `poetry add openai` |
| Anthropic client | `poetry add anthropic` |
| HTTP client (preferred) | `poetry add httpx` |
| Dev tools | `poetry add --group dev pytest ruff` |

`poetry add` updates `pyproject.toml` and `poetry.lock`. Do not edit `poetry.lock` by hand.

## Install From Lockfile

```bash
poetry install
```

In CI, prefer the deterministic flag:

```bash
poetry install --no-root --sync
```

Regenerate the lockfile only when intentionally bumping deps:

```bash
poetry lock
```

## Run the Agent

```bash
poetry run python agent.py
```

For other commands:

```bash
poetry run pytest
poetry run ruff check .
```

`poetry shell` opens an interactive shell inside the project venv if you prefer activated mode. `poetry run` is recommended for one-shot commands and CI.

## Optional `requirements.txt` Mirror

For deployment targets that only accept `requirements.txt`:

```bash
poetry export -f requirements.txt -o requirements.txt --without-hashes
```

Regenerate after every `poetry add` / `poetry lock`.

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

# Poetry / virtualenv
.venv/
.poetry-cache/
dist/
build/

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
poetry install
cp .env.example .env
# fill in AGENT_SEED and any protocol secrets
poetry run python agent.py
```
````

---

## Hard Rules

- Always use `poetry add` to add deps; never edit `poetry.lock` by hand.
- Always use `poetry run` (or an active `poetry shell`) to execute project code; never call the system `python` directly.
- Always pin Python with `python = "^3.11"` (or higher) in `[tool.poetry.dependencies]`.
- Always commit `pyproject.toml` and `poetry.lock`.
- Never run `python -m venv` in a Poetry project; let Poetry manage the venv via `poetry env use`.
- Never mix Poetry with `uv` in the same project. If both lockfiles exist, surface the conflict and stop.
- Use `poetry env use python3.11` to avoid silently inheriting the system Python.

## Composition With Protocol Skills

When a protocol skill needs a new dependency:

1. Use the table above to map protocol → package.
2. Add it with `poetry add <pkg>` (or `--group dev` for tooling).
3. Confirm `poetry.lock` updated.
4. Continue with the protocol skill's code generation.

This skill does not generate any agent code itself — it only owns environment setup commands.
