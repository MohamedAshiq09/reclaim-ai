---
name: stripe-payment-protocol
description: Self-contained recipe for adding Stripe Checkout-backed payments to a Fetch.ai uAgent alongside Chat Protocol. Includes complete copy-paste-ready code for the Stripe helper, payment protocol with handlers, chat protocol that triggers payment, agent entrypoint, and `.env`. Covers RequestPayment / CommitPayment / CompletePayment / RejectPayment, server-side verification, idempotency, and dynamic pricing. Use when adding card payments to a uAgent, gating chat actions behind payment, or wiring `payment_protocol_spec` next to `chat_protocol_spec`.
---

# Stripe Payment Protocol (Fetch.ai uAgents)

## Purpose

Give the coding agent everything it needs — file layout, full code, env vars — to add a working **Stripe-backed payment protocol** to a Fetch.ai uAgent that also speaks Chat Protocol. No external doc lookup required.

## When to Use

- Adding card/Stripe payments to an existing chat-capable uAgent
- Implementing `uagents_core.contrib.protocols.payment` as a seller
- Gating an expensive chat action (image gen, video gen, paid API call, etc.) behind payment
- Any task referencing `RequestPayment`, `CommitPayment`, `CompletePayment`, `RejectPayment`, or `payment_protocol_spec` together with Stripe

## When NOT to Use

- Pure web-app Stripe integration (no uAgents)
- Crypto-only payments (FET, USDC) — use the relevant skill instead
- Mock / pseudo payment flows
- Subscriptions — this skill targets one-time Checkout Sessions in `mode="payment"`

---

## Package Setup

Before running install commands, creating `pyproject.toml`, or generating `.env.example` / `.gitignore`, check which **package setup skill** is installed and defer to it:

- `uv-package` for `uv` projects
- `poetry-package` for Poetry projects
- `python-venv-package` for `venv` + `pip` projects
- `no-package` for code-only mode (no install commands)

This protocol skill only defines payment protocol and Stripe integration code. It does not own dependency installation, lockfile management, or virtualenv creation.

### Package Skill Precedence (mandatory)

Use this decision order before emitting any setup/install/run command:

1. Detect which package skills are actually available in the current session from this set only: `uv-package`, `no-package`, `poetry-package`, `python-venv-package`.
2. If the user explicitly asks for one of those managers and the matching skill is available, use it.
3. Otherwise, if repository signals are present, select the matching available skill:
   - `uv.lock` or `[tool.uv]` -> `uv-package`
   - `poetry.lock` or `[tool.poetry]` -> `poetry-package`
   - `requirements.txt` / existing `.venv` conventions -> `python-venv-package`
4. If no manager is detectable, choose one available skill and stay consistent for the full response. Prefer this fallback order: `uv-package` -> `poetry-package` -> `python-venv-package` -> `no-package`.
5. Never emit commands for a package skill that is not available.

When a package skill is active, all dependency/setup/run instructions must come from that skill only:

- `uv-package` -> `uv add ...`, `uv run python agent.py`
- `poetry-package` -> `poetry add ...`, `poetry run python agent.py`
- `python-venv-package` -> `pip install ...` (and project's venv flow)
- `no-package` -> no install commands; only document dependencies

Extra runtime dependencies required by this skill on top of the base set: `stripe` (Stripe SDK) and `openai` (ASI:One default LLM client). Add them through whichever package skill is active:

| Active package skill | Command |
| --- | --- |
| `uv-package` | `uv add stripe openai` |
| `poetry-package` | `poetry add stripe openai` |
| `python-venv-package` | `pip install stripe openai && pip freeze > requirements.txt` |
| `no-package` | document `stripe` and `openai` in the project's `## Dependencies` block |

---

## File Layout

Build this structure exactly. Every file has a single concern:

```
agent.py                       # entrypoint: load env, create Agent, include both protocols
protocols/
  __init__.py                  # empty
  chat_proto.py                # chat protocol + handler that triggers payment when needed
  payment_proto.py             # payment protocol + handlers + request_payment_from_user helper
stripe_payments/
  __init__.py                  # empty
  checkout.py                  # ONLY place that touches the Stripe SDK
.env.example
```

Hard separation — never mix:

- Stripe SDK calls live **only** in `stripe_payments/checkout.py`.
- `RequestPayment` / `CommitPayment` / `RejectPayment` / `CompletePayment` handling lives **only** in `protocols/payment_proto.py`.
- `ChatMessage` handling lives **only** in `protocols/chat_proto.py`.
- `agent.py` only loads env, creates the Agent, calls `set_agent_wallet`, and `include`s both protocols.

> Naming note: do **not** name the local folder `stripe/`. A top-level `stripe/` package shadows the official `stripe` SDK on `import stripe`, breaking every Stripe API call. Use `stripe_payments/` (or any other name except `stripe`).

---

## The Payment Flow

```
ChatMessage arrives
  protocols/chat_proto.py: handle_chat
    └─ if user already has verified_payment for this session -> fulfill paid action
    └─ if request needs payment -> call request_payment_from_user(...)

request_payment_from_user (in protocols/payment_proto.py)
  └─ stripe_payments.checkout.create_embedded_checkout_session(...)
  └─ persist user's prompt under "chat_prompt:<user>:<chat_session_id>"
  └─ build RequestPayment(
       accepted_funds=[Funds(currency="USD", amount=..., payment_method="stripe")],
       metadata={"stripe": { client_secret, checkout_session_id, publishable_key, ... }},
     )
  └─ ctx.send(user_address, RequestPayment)
  └─ ctx.storage.set("payment_request:pending:<user>:<chat_session_id>", ...)
  └─ ctx.storage.set("payment_request:by_checkout:<checkout_session_id>", ...)

User completes embedded Checkout in the client UI

CommitPayment(transaction_id=<checkout_session_id>, funds.payment_method="stripe") arrives
  protocols/payment_proto.py: on_commit
    ├─ idempotency check:
    │    already processed?
    │      ├─ paid action already fulfilled -> re-send CompletePayment
    │      └─ not fulfilled yet -> re-send CompletePayment + resume fulfillment
    ├─ stripe_payments.checkout.verify_checkout_session_paid(transaction_id)
    │     └─ stripe.checkout.Session.retrieve(...).payment_status == "paid"
    ├─ verified -> resolve chat session id with fallback chain:
    │              Stripe metadata.session_id
    │                -> storage["payment_request:by_checkout:<cs_id>"].chat_session_id
    │                -> ctx.session
    │          -> ctx.send(sender, CompletePayment(transaction_id=...))
    │          -> mark verified_payment for that chat session
    │          -> read storage["chat_prompt:<sender>:<session_id>"]
    │          -> await run_paid_action(ctx, sender, session_id, text=prompt)
    └─ not verified -> ctx.send(sender, RejectPayment(reason=...))

If buyer/UI sends RejectPayment -> on_reject clears pending state and notifies via chat
```

The user-facing UI uses `metadata["stripe"]["client_secret"]` to mount Stripe's embedded Checkout. The agent never collects card data itself.

---

## Directional Logging Contract

Every agent generated from this skill must emit structured logs so the user can trace the payment lifecycle directly from CLI output. This makes production debugging tractable and keeps chat + payment flows auditable end-to-end.

### Required tags

- `[inbound]` — log the moment a protocol message is received (`ChatMessage`, `ChatAcknowledgement`, `CommitPayment`, `RejectPayment`), **before** any processing. Always include message type + sender.
- `[outbound]` — log immediately **before** every `ctx.send(...)`. Always include message type + recipient.
- `[state]` — log significant storage transitions (pending request set/cleared, verified-payment set/cleared, duplicate short-circuits).
- `[payment]` — domain-specific events (Stripe checkout created, Stripe verify result, amount mismatch).

### Redaction rules

- Never log `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, the Stripe `client_secret`, or full `msg.metadata` dumps.
- Log only the Checkout Session ID (`cs_...`), the `payment_method`, amount + currency, and `payment_status`.
- Truncate user-supplied description / chat text at ~120 chars.

### Helpers (put in `protocols/payment_proto.py` and `protocols/chat_proto.py`)

```python
def log_inbound(ctx: Context, msg_type: str, sender: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[inbound] {msg_type} from {sender}{suffix}")


def log_outbound(ctx: Context, msg_type: str, recipient: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[outbound] {msg_type} -> {recipient}{suffix}")


def log_state(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[state] {event}{suffix}")
```

Every `ctx.send(...)` in payment and chat code must be preceded by `log_outbound(...)`. Every `@payment_proto.on_message(...)` / `@chat_proto.on_message(...)` handler must start with `log_inbound(...)`.

---

## File 1 — `stripe_payments/checkout.py`

The only file that touches the Stripe SDK. Pure functions, no `ctx`, no protocol types.

```python
import os
import time
from typing import Any
from uuid import uuid4


def _stripe_sdk():
    try:
        import stripe
        return stripe
    except Exception:
        return None


def is_stripe_configured() -> bool:
    sdk = _stripe_sdk()
    return bool(sdk and os.getenv("STRIPE_SECRET_KEY") and os.getenv("STRIPE_PUBLISHABLE_KEY"))


def stripe_metadata_to_dict(metadata: Any) -> dict[str, Any]:
    """Stripe returns metadata as a StripeObject in some SDK versions, not a dict."""
    if not metadata:
        return {}
    if isinstance(metadata, dict):
        return metadata
    if hasattr(metadata, "to_dict_recursive"):
        return metadata.to_dict_recursive()
    try:
        return dict(metadata)
    except Exception:
        return {}


def create_embedded_checkout_session(
    *,
    user_address: str,
    chat_session_id: str,
    description: str,
    payment_request_id: str | None = None,
    amount_cents_override: int | None = None,
) -> dict[str, Any] | None:
    sdk = _stripe_sdk()
    if not sdk:
        return None
    secret = os.getenv("STRIPE_SECRET_KEY")
    publishable = os.getenv("STRIPE_PUBLISHABLE_KEY")
    if not (secret and publishable):
        return None
    sdk.api_key = secret

    price_id = (os.getenv("STRIPE_PRICE_ID") or "").strip()
    amount_cents = amount_cents_override if amount_cents_override is not None else int(
        os.getenv("STRIPE_AMOUNT_CENTS", "100")
    )
    currency = (os.getenv("STRIPE_CURRENCY") or "usd").strip().lower()
    product_name = os.getenv("STRIPE_PRODUCT_NAME", "Agent service")
    success_url = os.getenv("STRIPE_SUCCESS_URL", "https://agentverse.ai/payment-success")

    expires_in = max(1800, min(24 * 60 * 60, int(os.getenv("STRIPE_CHECKOUT_EXPIRES_SECONDS", "1800"))))
    expires_at = int(time.time()) + expires_in

    payment_reference = f"{user_address}:{chat_session_id}:{uuid4().hex[:8]}"
    return_url = (
        f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}"
        f"&chat_session_id={chat_session_id}&user={user_address}"
    )
    if payment_request_id:
        return_url += f"&payment_request_id={payment_request_id}"

    line_items = (
        [{"price": price_id, "quantity": 1}]
        if price_id
        else [{
            "price_data": {
                "currency": currency,
                "product_data": {"name": product_name, "description": description},
                "unit_amount": amount_cents,
            },
            "quantity": 1,
        }]
    )

    idem_parts = [
        user_address,
        chat_session_id,
        payment_request_id or "",
        "price" if price_id else "inline",
        str(amount_cents),
    ]
    base_idempotency_key = ":".join(idem_parts)

    base_kwargs: dict[str, Any] = {
        "redirect_on_completion": "if_required",
        "payment_method_types": ["card"],
        "mode": "payment",
        "line_items": line_items,
        "return_url": return_url,
        "expires_at": expires_at,
        "metadata": {
            "user_address": user_address,
            "session_id": chat_session_id,
            "payment_reference": payment_reference,
        },
    }

    # Stripe API 2026-03-25 ("Dahlia") renamed ui_mode "embedded" -> "embedded_page".
    # Default to the new value; fall back to the legacy value if the account is
    # pinned to an older API version. Each attempt uses its own idempotency key
    # so Stripe doesn't replay a cached 400 from the first try.
    ui_mode_attempts = [
        ("embedded_page", base_idempotency_key + ":embedded_page"),
        ("embedded", base_idempotency_key + ":embedded"),
    ]
    last_error: str | None = None

    for ui_mode, idem_key in ui_mode_attempts:
        try:
            session = sdk.checkout.Session.create(
                ui_mode=ui_mode,
                idempotency_key=idem_key[:255],
                **base_kwargs,
            )
            return {
                "client_secret": session.client_secret,
                "id": session.id,
                "publishable_key": publishable,
                "amount_cents": amount_cents,
                "currency": currency,
                "ui_mode": ui_mode,
            }
        except sdk.error.InvalidRequestError as exc:
            err = str(exc).lower()
            last_error = str(exc)
            if "ui_mode" in err and (
                "no longer supported" in err
                or "invalid value" in err
                or "is not a valid" in err
            ):
                continue  # try the other ui_mode value
            return {"error": str(exc)}
        except Exception as exc:
            return {"error": str(exc)}

    return {"error": last_error or "Could not create Checkout Session"}


def verify_checkout_session_paid(checkout_session_id: str) -> dict[str, Any]:
    sdk = _stripe_sdk()
    if not sdk:
        return {"verified": False, "error": "stripe SDK not installed"}
    secret = os.getenv("STRIPE_SECRET_KEY")
    if not secret:
        return {"verified": False, "error": "Stripe not configured"}
    sdk.api_key = secret
    try:
        s = sdk.checkout.Session.retrieve(checkout_session_id)
        metadata = stripe_metadata_to_dict(getattr(s, "metadata", {}) or {})
        return {
            "verified": getattr(s, "payment_status", None) == "paid",
            "checkout_session_id": checkout_session_id,
            "status": getattr(s, "payment_status", None),
            "amount_total": getattr(s, "amount_total", None),
            "currency": getattr(s, "currency", None),
            "metadata": metadata,
        }
    except Exception as exc:
        return {"verified": False, "error": str(exc)}
```

---

## File 2 — `protocols/payment_proto.py`

Owns the seller-side payment protocol, the `RequestPayment` builder, and both message handlers. Imports the Stripe helper from `stripe_payments.checkout` and never touches the Stripe SDK directly.

```python
import os
from datetime import datetime, timezone
from uuid import uuid4

from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import ChatMessage, TextContent
from uagents_core.contrib.protocols.payment import (
    Funds,
    RequestPayment,
    CommitPayment,
    CompletePayment,
    RejectPayment,
    payment_protocol_spec,
)

from stripe_payments.checkout import (
    create_embedded_checkout_session,
    is_stripe_configured,
    verify_checkout_session_paid,
)

payment_proto = Protocol(spec=payment_protocol_spec, role="seller")


def _env_int(name: str, default: int) -> int:
    """Safe int parsing for env vars; falls back to default on missing/garbage values
    instead of raising at module import time."""
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


STRIPE_AMOUNT_CENTS = _env_int("STRIPE_AMOUNT_CENTS", 100)
STRIPE_FUNDS = Funds(
    currency="USD",
    amount=f"{STRIPE_AMOUNT_CENTS / 100:.2f}",
    payment_method="stripe",
)

_agent_wallet = None


def set_agent_wallet(wallet) -> None:
    global _agent_wallet
    _agent_wallet = wallet


def log_inbound(ctx: Context, msg_type: str, sender: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[inbound] {msg_type} from {sender}{suffix}")


def log_outbound(ctx: Context, msg_type: str, recipient: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[outbound] {msg_type} -> {recipient}{suffix}")


def log_state(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {details}" if details else ""
    ctx.logger.info(f"[state] {event}{suffix}")


def metadata_value(metadata, key: str, default: str = "") -> str:
    """Stripe metadata may be a StripeObject; normalize reads to avoid AttributeError."""
    if isinstance(metadata, dict):
        return str(metadata.get(key) or default)
    if hasattr(metadata, "to_dict_recursive"):
        return str(metadata.to_dict_recursive().get(key) or default)
    return str(getattr(metadata, key, default) or default)


def _lookup_session_id_by_checkout(ctx: Context, tx_id: str) -> str:
    """Recover the chat session id for a Stripe Checkout Session id.

    Stripe metadata occasionally arrives empty (legacy sessions, custom UIs
    that strip metadata). The pending request mapping persisted in
    `request_payment_from_user` is the canonical fallback.
    """
    try:
        rec = ctx.storage.get(f"payment_request:by_checkout:{tx_id}") or {}
    except Exception:
        return ""
    if isinstance(rec, dict):
        return str(rec.get("chat_session_id") or "")
    return ""


def _chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


def _fulfilled_key(user_address: str, session_id: str, tx_id: str) -> str:
    return f"payment:fulfilled:{user_address}:{session_id}:{tx_id}"


async def request_payment_from_user(
    ctx: Context,
    user_address: str,
    chat_session_id: str,
    description: str,
    text: str | None = None,
) -> None:
    """Called from the chat layer when a paid action is requested.

    `text` is the user's original prompt. We persist it so `on_commit` can
    fulfill the request after Stripe verifies the payment, without depending
    on Stripe's metadata round-trip.
    """
    pending_key = f"payment_request:pending:{user_address}:{chat_session_id}"
    prompt_key = f"chat_prompt:{user_address}:{chat_session_id}"

    # Always refresh the persisted prompt so the latest paid request wins.
    try:
        ctx.storage.set(prompt_key, text or "")
    except Exception as e:
        ctx.logger.warning(f"[payment] failed to persist chat prompt: {e}")

    if ctx.storage.has(pending_key):
        log_state(ctx, "pending_request_exists", f"user={user_address} session={chat_session_id}")
        return  # one pending RequestPayment per chat session

    if not is_stripe_configured():
        ctx.logger.warning("[payment] stripe not configured; cannot request payment")
        reply = _chat("Card payments are not available right now.")
        log_outbound(ctx, "ChatMessage", user_address, "stripe_unavailable")
        await ctx.send(user_address, reply)
        return

    checkout = create_embedded_checkout_session(
        user_address=user_address,
        chat_session_id=chat_session_id,
        description=description,
        payment_request_id=uuid4().hex,
    )
    if not checkout or checkout.get("error") or not checkout.get("client_secret"):
        err = (checkout or {}).get("error") or "unknown error"
        ctx.logger.error(f"[payment] stripe checkout create failed: {err}")
        reply = _chat("Could not create Stripe checkout. Please try again.")
        log_outbound(ctx, "ChatMessage", user_address, "stripe_create_failed")
        await ctx.send(user_address, reply)
        return

    ctx.logger.info(
        f"[payment] stripe checkout created cs_id={checkout['id']} "
        f"amount_cents={checkout['amount_cents']} currency={checkout['currency']} "
        f"ui_mode={checkout.get('ui_mode')}"
    )

    metadata = {
        "agent": ctx.agent.name,
        "stripe": {
            # NOTE: the literal string "embedded" here is the Agentverse UI
            # contract (it tells the frontend to render the embedded Stripe
            # Checkout widget). It is NOT the Stripe API enum. The Stripe API
            # uses "embedded_page" / "embedded" — see stripe_payments/checkout.py.
            "ui_mode": "embedded",
            "publishable_key": checkout["publishable_key"],
            "client_secret": checkout["client_secret"],
            "checkout_session_id": checkout["id"],
            "amount_cents": checkout["amount_cents"],
            "currency": checkout["currency"],
        },
    }

    recipient = str(_agent_wallet.address()) if _agent_wallet else ctx.agent.address
    msg = RequestPayment(
        accepted_funds=[STRIPE_FUNDS],
        recipient=recipient,
        deadline_seconds=_env_int("CHECKOUT_DEADLINE_SECONDS", 300),
        reference=str(uuid4()),
        description=description,
        metadata=metadata,
    )
    log_outbound(
        ctx, "RequestPayment", user_address,
        f"cs_id={checkout['id']} amount_cents={checkout['amount_cents']} currency={checkout['currency']}",
    )
    await ctx.send(user_address, msg)
    ctx.storage.set(pending_key, {"checkout_session_id": checkout["id"]})
    ctx.storage.set(
        f"payment_request:by_checkout:{checkout['id']}",
        {
            "user_address": user_address,
            "chat_session_id": chat_session_id,
            "amount_cents": int(checkout["amount_cents"]),
            "currency": str(checkout["currency"]).lower(),
        },
    )
    log_state(ctx, "pending_request_saved", f"user={user_address} session={chat_session_id} cs_id={checkout['id']}")


@payment_proto.on_message(CommitPayment)
async def on_commit(ctx: Context, sender: str, msg: CommitPayment):
    tx_id = str(getattr(msg, "transaction_id", "") or "")
    method = str(getattr(msg.funds, "payment_method", "") or "")
    log_inbound(ctx, "CommitPayment", sender, f"tx_id={tx_id or 'MISSING'} method={method}")

    if not tx_id:
        log_outbound(ctx, "RejectPayment", sender, "reason=missing_tx_id")
        await ctx.send(sender, RejectPayment(reason="Missing Stripe checkout session id"))
        return

    processed_key = f"payments:processed:{sender}:{tx_id}"
    if ctx.storage.get(processed_key):
        # Replay-safe fulfillment: duplicate CommitPayment should not mint/verify
        # again, but if fulfillment never completed we must resume it.
        metadata = verify_checkout_session_paid(tx_id).get("metadata") or {}
        session_id = (
            metadata_value(metadata, "session_id")
            or _lookup_session_id_by_checkout(ctx, tx_id)
            or str(ctx.session)
        )
        fulfilled_key = _fulfilled_key(sender, session_id, tx_id)
        log_state(
            ctx,
            "duplicate_commit",
            f"tx_id={tx_id} fulfilled={bool(ctx.storage.get(fulfilled_key))}",
        )
        log_outbound(ctx, "CompletePayment", sender, f"tx_id={tx_id} idempotent_replay=true")
        await ctx.send(sender, CompletePayment(transaction_id=tx_id))
        if ctx.storage.get(fulfilled_key):
            return
        try:
            prompt = str(ctx.storage.get(f"chat_prompt:{sender}:{session_id}") or "")
        except Exception:
            prompt = ""
        try:
            from protocols.chat_proto import run_paid_action
            await run_paid_action(ctx, sender, session_id, text=prompt)
            ctx.storage.set(fulfilled_key, True)
            log_state(ctx, "post_payment_fulfilled", f"user={sender} session={session_id} tx_id={tx_id} replay=true")
        except Exception as e:
            ctx.logger.exception(f"[payment] replay fulfillment failed: {e}")
        return

    if method != "stripe":
        log_outbound(ctx, "RejectPayment", sender, f"reason=unsupported_method method={method}")
        await ctx.send(sender, RejectPayment(reason="Unsupported payment method (expected stripe)."))
        return

    result = verify_checkout_session_paid(tx_id)
    ctx.logger.info(
        f"[payment] stripe verify tx_id={tx_id} verified={result.get('verified')} "
        f"status={result.get('status')} amount_total={result.get('amount_total')} "
        f"currency={result.get('currency')}"
    )
    if not result.get("verified"):
        reason = result.get("error") or "Stripe payment not completed yet."
        log_outbound(ctx, "RejectPayment", sender, f"reason=not_verified tx_id={tx_id}")
        await ctx.send(sender, RejectPayment(reason=reason))
        return

    # Resolve the chat session id with a robust fallback chain so a verified
    # payment never gets rejected just because Stripe's metadata round-trip
    # came back empty.
    metadata = result.get("metadata") or {}
    session_id = (
        metadata_value(metadata, "session_id")
        or _lookup_session_id_by_checkout(ctx, tx_id)
        or str(ctx.session)
    )
    # Prevent cross-user checkout reuse and assert expected charge shape.
    checkout_ref = ctx.storage.get(f"payment_request:by_checkout:{tx_id}") or {}
    if isinstance(checkout_ref, dict):
        expected_user = str(checkout_ref.get("user_address") or "")
        if expected_user and expected_user != sender:
            log_outbound(ctx, "RejectPayment", sender, f"reason=checkout_owner_mismatch tx_id={tx_id}")
            await ctx.send(sender, RejectPayment(reason="Checkout session does not belong to this user."))
            return
        expected_amount = checkout_ref.get("amount_cents")
        expected_currency = str(checkout_ref.get("currency") or "").lower()
        actual_amount = result.get("amount_total")
        actual_currency = str(result.get("currency") or "").lower()
        if isinstance(expected_amount, int) and actual_amount is not None and int(actual_amount) != expected_amount:
            log_outbound(ctx, "RejectPayment", sender, f"reason=amount_mismatch tx_id={tx_id}")
            await ctx.send(sender, RejectPayment(reason="Stripe amount mismatch."))
            return
        if expected_currency and actual_currency and actual_currency != expected_currency:
            log_outbound(ctx, "RejectPayment", sender, f"reason=currency_mismatch tx_id={tx_id}")
            await ctx.send(sender, RejectPayment(reason="Stripe currency mismatch."))
            return
    log_state(ctx, "session_id_resolved", f"tx_id={tx_id} session={session_id}")

    ctx.storage.set(processed_key, True)
    ctx.storage.set(f"{sender}:{session_id}:verified_payment", True)
    ctx.storage.remove(f"payment_request:pending:{sender}:{session_id}")
    ctx.storage.remove(f"payment_request:by_checkout:{tx_id}")
    log_state(ctx, "payment_verified", f"user={sender} session={session_id} tx_id={tx_id}")

    log_outbound(ctx, "CompletePayment", sender, f"tx_id={tx_id}")
    await ctx.send(sender, CompletePayment(transaction_id=tx_id))

    # Auto-fulfill: read the user's original prompt and run the paid action.
    # Without this, the agent stalls after CompletePayment and the user never
    # gets the result they paid for.
    fulfilled_key = _fulfilled_key(sender, session_id, tx_id)
    try:
        prompt = str(ctx.storage.get(f"chat_prompt:{sender}:{session_id}") or "")
    except Exception:
        prompt = ""
    try:
        from protocols.chat_proto import run_paid_action
        await run_paid_action(ctx, sender, session_id, text=prompt)
        ctx.storage.set(fulfilled_key, True)
        log_state(ctx, "post_payment_fulfilled", f"user={sender} session={session_id} tx_id={tx_id}")
    except Exception as e:
        ctx.logger.exception(f"[payment] post-payment fulfillment failed: {e}")
        fail = _chat("Payment received, but generating the result failed. Please retry.")
        log_outbound(ctx, "ChatMessage", sender, "post_payment_fulfillment_failed")
        await ctx.send(sender, fail)


@payment_proto.on_message(RejectPayment)
async def on_reject(ctx: Context, sender: str, msg: RejectPayment):
    reason = str(getattr(msg, "reason", "") or "no reason")
    log_inbound(ctx, "RejectPayment", sender, f"reason={reason[:120]}")

    session_id = str(ctx.session)
    try:
        ctx.storage.remove(f"payment_request:pending:{sender}:{session_id}")
        log_state(ctx, "pending_request_cleared", f"user={sender} session={session_id}")
    except Exception:
        pass

    reply = _chat("Payment was not completed. Reply if you want to try again and I'll send a new payment request.")
    log_outbound(ctx, "ChatMessage", sender, "payment_reject_ack")
    await ctx.send(sender, reply)
```

---

## File 3 — `protocols/chat_proto.py`

Owns the Chat Protocol and the chat handler. Imports `request_payment_from_user` from `payment_proto` to trigger the paid flow when the user asks for a paid action. No Stripe SDK and no payment-protocol message types here.

```python
from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4

from openai import OpenAI
from uagents import Context, Protocol
from uagents_core.contrib.protocols.chat import (
    ChatAcknowledgement,
    ChatMessage,
    TextContent,
    chat_protocol_spec,
)

from protocols.payment_proto import (
    log_inbound,
    log_outbound,
    log_state,
    request_payment_from_user,
)

chat_proto = Protocol(spec=chat_protocol_spec)

ASI_ONE_BASE_URL = "https://api.asi1.ai/v1"
ASI_ONE_MODEL = os.getenv("ASI_ONE_MODEL", "asi1").strip() or "asi1"
ASI_ONE_SYSTEM_PROMPT = (
    os.getenv("ASI_ONE_SYSTEM_PROMPT")
    or "You are a helpful, precise assistant. Answer the user's request directly."
)

_asi_client: OpenAI | None = None


def _get_asi_client() -> OpenAI:
    global _asi_client
    if _asi_client is None:
        _asi_client = OpenAI(
            api_key=os.getenv("ASI_ONE_API_KEY"),
            base_url=ASI_ONE_BASE_URL,
        )
    return _asi_client


def _call_asi_one(prompt: str, *, session_id: str) -> str:
    response = _get_asi_client().chat.completions.create(
        model=ASI_ONE_MODEL,
        messages=[
            {"role": "system", "content": ASI_ONE_SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=1000,
        extra_headers={"x-session-id": session_id} if session_id else None,
    )
    return response.choices[0].message.content or "(no response)"


def create_text_chat(text: str) -> ChatMessage:
    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[TextContent(type="text", text=text)],
    )


def _user_text(msg: ChatMessage) -> str:
    parts = [c.text for c in msg.content if isinstance(c, TextContent)]
    return " ".join(parts).strip()


def _is_paid_request(text: str) -> bool:
    """Replace this stub with the agent's real 'paid action requested' detector."""
    if not text:
        return False
    return True  # default: every non-empty user message requires payment


@chat_proto.on_message(ChatMessage)
async def handle_chat(ctx: Context, sender: str, msg: ChatMessage):
    log_inbound(ctx, "ChatMessage", sender, f"msg_id={msg.msg_id}")

    ack = ChatAcknowledgement(
        timestamp=datetime.now(timezone.utc),
        acknowledged_msg_id=msg.msg_id,
    )
    log_outbound(ctx, "ChatAcknowledgement", sender, f"acknowledged_msg_id={msg.msg_id}")
    await ctx.send(sender, ack)

    text = _user_text(msg)
    session_id = str(ctx.session)
    already_paid = bool(ctx.storage.get(f"{sender}:{session_id}:verified_payment"))
    ctx.logger.info(f"[inbound] text from {sender}: {text[:120]!r} already_paid={already_paid}")

    if already_paid:
        # Reuse the verified flag for follow-up messages in the same session.
        # Trade-off: one paid session keeps serving until ctx.session changes.
        # If you require pay-per-message, remove the flag here and persist a
        # counter instead.
        await run_paid_action(ctx, sender, session_id, text=text)
        return

    if _is_paid_request(text):
        await request_payment_from_user(
            ctx, sender,
            chat_session_id=session_id,
            description="Payment required to continue.",
            text=text,
        )
        notice = create_text_chat("Once payment completes, I'll reply here with your result.")
        log_outbound(ctx, "ChatMessage", sender, "awaiting_payment_notice")
        await ctx.send(sender, notice)
        return

    greet = create_text_chat("How can I help?")
    log_outbound(ctx, "ChatMessage", sender, "default_greeting")
    await ctx.send(sender, greet)


@chat_proto.on_message(ChatAcknowledgement)
async def handle_chat_ack(ctx: Context, sender: str, msg: ChatAcknowledgement):
    log_inbound(ctx, "ChatAcknowledgement", sender, f"acknowledged_msg_id={msg.acknowledged_msg_id}")


async def run_paid_action(
    ctx: Context,
    user_address: str,
    session_id: str,
    text: str | None = None,
) -> None:
    """Run the paid action and reply on the chat protocol.

    Default implementation: route the prompt to ASI:One. Replace with image
    gen, video gen, a deterministic API call, etc., when the use case is not
    a chat completion.
    """
    prompt = (text or "").strip() or "Say hello."
    try:
        reply_text = await asyncio.to_thread(_call_asi_one, prompt, session_id=session_id)
    except Exception as e:
        ctx.logger.exception(f"[payment] ASI:One call failed: {e}")
        reply_text = "Sorry — the assistant call failed. Please try again."
    reply = create_text_chat(reply_text)
    log_outbound(ctx, "ChatMessage", user_address, "paid_action_result")
    await ctx.send(user_address, reply)
```

---

## Default LLM (ASI:One)

`run_paid_action(...)` ships as a working ASI:One call out of the box. ASI:One is the **default** LLM for any agent scaffolded by this skill: it is OpenAI Chat Completions API-compatible, so the standard `openai` Python SDK works unchanged with `base_url` pointed at `https://api.asi1.ai/v1`. The wiring is already shown inline in File 3 — this section explains when to deviate.

### Decision: which LLM to use

Walk the rules in order; pick the first match and stop.

1. **Does the paid action actually need an LLM?** If `run_paid_action` is image gen via a fixed endpoint, a deterministic API call, an echo, or anything non-LLM, replace the ASI:One body with the deterministic call and drop the `openai` import + `ASI_ONE_API_KEY`.
2. **Did the user explicitly name a different provider or model?** (e.g. `openai`, `gpt-4o`, `gpt-5`, `claude-3.5-sonnet`, `anthropic`, `gemini`, `groq`, `ollama`, `together`, `mistral`, etc.) — use exactly that and remove the ASI:One client. Treat `asi1`, `asi:one`, `asi-one`, `asione`, "ASI", or "ASI One" as an explicit confirmation of the default.
3. **Otherwise** — keep ASI:One. Do not require user opt-in.

When extending an existing project that already wires up a different provider (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `langchain_*`, an `llm.py` wrapper, etc.), reuse that wiring instead of adding ASI:One on top — but for a **new** scaffold, ASI:One is the answer.

### Required env var (always)

`.env.example` always includes `ASI_ONE_API_KEY`. Validate it at agent startup the same way `AGENT_SEED` is validated so the agent fails fast instead of silently 401-ing on the first paid request:

```python
ASI_ONE_API_KEY = _required("ASI_ONE_API_KEY")
```

Do not add `OPENAI_API_KEY` (different provider) and never invent placeholder keys.

### Dependency (always)

Always add the official `openai` Python SDK alongside `uagents` / `uagents-core`. Route the install through the active package skill (`uv add openai`, `poetry add openai`, `pip install openai`, or document-only for `no-package`). Do not pin a version unless the project already pins others.

### Optional knobs (use only when the use case needs them)

ASI:One accepts every standard OpenAI parameter (`temperature`, `top_p`, `max_tokens`, `presence_penalty`, `frequency_penalty`, `stream`) plus two extras exposed via the OpenAI SDK's escape hatches:

- **Web search** — `extra_body={"web_search": True}` to let the model browse, `False` to force it off. Omit otherwise.
- **Agentic session persistence** — `extra_headers={"x-session-id": session_id}` to keep multi-turn agentic state across calls. Use a stable string per chat session (the chat session id is a natural fit).

### Streaming

ASI:One occasionally emits chunks with no `choices` or empty `delta.content`. If streaming, guard every chunk:

```python
for chunk in response:
    if (
        getattr(chunk, "choices", None)
        and chunk.choices
        and getattr(chunk.choices[0], "delta", None)
        and chunk.choices[0].delta.content
    ):
        partial = chunk.choices[0].delta.content
```

For a paid-action reply, batch streamed pieces into a single `ChatMessage` (or send incremental `ChatMessage`s with new `msg_id`s — the chat protocol does not support partial updates of an existing message).

### Response shape

- `response.choices[0].message.content` — main reply text. Always read this for plain chat.
- `response.usage` — token usage (`prompt_tokens`, `completion_tokens`, `total_tokens`).
- `response.model` — model name echoed back.
- ASI:One-specific fields (read defensively with `getattr`, may be absent): `executable_data` (Agentverse agent calls / tool manifests), `intermediate_steps` (multi-step reasoning trace), `thought` (model reasoning).

### Hard rules for ASI:One

- Never hardcode the API key — always `os.getenv("ASI_ONE_API_KEY")`.
- Never log the API key, full streamed text, or `intermediate_steps` / `thought` payloads — they may carry tool arguments or sensitive context. Log lengths only, consistent with the Directional Logging Contract above.
- `base_url` is always exactly `https://api.asi1.ai/v1`. Do not call `https://api.openai.com` while routing to ASI:One.
- Do not silently fall back to another provider if ASI:One is unreachable — surface the error and let the user decide. Silent fallback hides outages and bills the wrong account.
- Keep the LLM call inside `protocols/chat_proto.py` (in `run_paid_action`). Do not put it in `payment_proto.py` or in `stripe_payments/checkout.py`.

---

## File 4 — `agent.py`

Tiny entrypoint. Loads env, creates the Agent, sets the wallet hook, includes both protocols. No business logic.

```python
import os

from dotenv import load_dotenv
load_dotenv()

from uagents import Agent
from uagents.setup import fund_agent_if_low

from protocols.chat_proto import chat_proto
from protocols.payment_proto import payment_proto, set_agent_wallet


def _required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


# Validate critical env vars up front so the agent fails fast instead of
# 401-ing on the first paid request or breaking after Stripe has already
# charged a card.
AGENT_SEED = _required("AGENT_SEED")
ASI_ONE_API_KEY = _required("ASI_ONE_API_KEY")

# Development default: testnet. Switch to "mainnet" only when the user explicitly
# opts into a production deploy. This controls Almanac contract registration.
AGENT_NETWORK = (os.getenv("AGENT_NETWORK") or "testnet").strip().lower()

agent = Agent(
    name=os.getenv("AGENT_NAME", "stripe_agent"),
    seed=AGENT_SEED,
    port=int(os.getenv("AGENT_PORT", "8000")),
    mailbox=True,
    agentverse=os.getenv("AGENTVERSE_URL", "https://agentverse.ai"),
    network=AGENT_NETWORK,
)

# REQUIRED on testnet: top up the agent wallet so Almanac registration succeeds.
# Without this, uagents logs:
#   WARNING: [uagents.registration] I do not have enough funds to register on Almanac contract
#   WARNING: [uagents.registration] To enable contract registration, send funds to wallet address: fetch1...
# fund_agent_if_low is a no-op once the wallet has enough testnet FET, so it is safe on every restart.
# On mainnet the operator funds the wallet themselves; do not call it.
if AGENT_NETWORK == "testnet":
    fund_agent_if_low(str(agent.wallet.address()))

set_agent_wallet(agent.wallet)

agent.include(chat_proto, publish_manifest=True)
agent.include(payment_proto, publish_manifest=True)


if __name__ == "__main__":
    agent.run()
```

`load_dotenv()` runs **before** `protocols/payment_proto.py` is imported so its module-level `os.getenv` reads the correct values.

---

## File 5 — `.env.example`

List every variable the code reads. Nothing else.

```
# Agent identity
AGENT_SEED=your_unique_seed_phrase_here
AGENT_NAME=stripe_agent
AGENT_PORT=8000
AGENTVERSE_URL=https://agentverse.ai
# Almanac registration network. "testnet" auto-funds the wallet via fund_agent_if_low
# and registers against the Fetch.ai testnet contract. Switch to "mainnet" only when
# going to production (the user is then responsible for funding the wallet).
AGENT_NETWORK=testnet

# Stripe (server-side keys — use TEST keys until going live)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
# Optional: pin a pre-created Stripe Price; otherwise inline price_data is used
STRIPE_PRICE_ID=
STRIPE_AMOUNT_CENTS=100
STRIPE_CURRENCY=usd
STRIPE_PRODUCT_NAME=Agent service
# Hosted page that closes the round-trip after Checkout
STRIPE_SUCCESS_URL=https://agentverse.ai/payment-success
STRIPE_CHECKOUT_EXPIRES_SECONDS=1800

# Payment protocol
CHECKOUT_DEADLINE_SECONDS=300

# --- Default LLM (ASI:One, OpenAI-compatible) ---
# ASI:One is the default LLM used by run_paid_action. Required at startup —
# the agent fails fast if missing. See "Default LLM (ASI:One)" above for the
# decision tree if you want to swap in a different provider.
ASI_ONE_API_KEY=
# Optional overrides:
ASI_ONE_MODEL=asi1
ASI_ONE_SYSTEM_PROMPT=You are a helpful, precise assistant. Answer the user's request directly.
```

Rules for env vars:

- Only list variables the code actually reads.
- Never commit a real `.env`. Add it to `.gitignore` if a `.gitignore` exists.
- Use **Stripe test keys** (`sk_test_...`, `pk_test_...`) by default. Only switch to live keys when explicitly asked, after the user confirms they have completed Stripe's go-live checklist.

---

## Stripe API Version Note (Dahlia, 2026-03-25)

There are **two unrelated `ui_mode` fields** in this skill — keep them straight or you will introduce a regression while trying to fix one:

| layer | where | values | controlled by |
| --- | --- | --- | --- |
| Stripe API parameter | `stripe.checkout.Session.create(ui_mode=...)` in `stripe_payments/checkout.py` | `embedded_page` (Dahlia+) or `embedded` (legacy accounts) | Stripe |
| Agentverse UI metadata | `RequestPayment.metadata["stripe"]["ui_mode"]` in `protocols/payment_proto.py` | always the literal `"embedded"` | Agentverse frontend |

Stripe shipped a breaking change on **2026-03-25** ("Dahlia") that renamed the Checkout Session `ui_mode` enum on the API side:

- `embedded` → `embedded_page`
- `hosted`   → `hosted_page`
- `custom`   → `elements`

Sending the old values to a Dahlia-or-later account fails with:

```
400 The ui_mode value `embedded` is no longer supported. Use `embedded_page` instead.
```

The helper in File 1 tries `embedded_page` first and falls back to `embedded` only if Stripe rejects the new value (i.e. the account is pinned to a pre-Dahlia API version). Each attempt uses its own idempotency key so Stripe doesn't replay a cached 400 from the first try.

The companion JS method was also renamed in Dahlia — frontends mounting the embedded checkout should now call `stripe.createEmbeddedCheckoutPage({ fetchClientSecret })` instead of `stripe.initEmbeddedCheckout(...)`.

**The Agentverse UI metadata stays `"embedded"` regardless of what Stripe's API accepted.** That exact literal in `metadata["stripe"]["ui_mode"]` is the contract the Agentverse frontend uses to pick the embedded-widget renderer — it is not a passthrough of Stripe's API enum.

### Patching an existing agent that still hits this error

In `stripe_payments/checkout.py` (the file calling Stripe), replace the single-attempt `Session.create(ui_mode="embedded", ...)` with the two-attempt loop in File 1 (`embedded_page` → `embedded` fallback, distinct idempotency keys).

In `protocols/payment_proto.py`, **leave `metadata["stripe"]["ui_mode"] = "embedded"` unchanged** — that string is what the Agentverse UI expects.

---

## Stripe Funds + Metadata Shape (reference)

```python
Funds(
    currency="USD",
    amount="1.00",          # string in major units, e.g. dollars
    payment_method="stripe" # required so the seller knows to verify via Stripe
)
```

The UI consumes `RequestPayment.metadata["stripe"]`:

```json
{
  "ui_mode": "embedded",
  "publishable_key": "pk_test_...",
  "client_secret": "cs_test_...",
  "checkout_session_id": "cs_test_...",
  "amount_cents": 100,
  "currency": "usd"
}
```

The `ui_mode` field here is the **Agentverse UI contract** — always the literal string `"embedded"`. It tells the frontend to render the embedded Stripe Checkout widget. It is NOT the same as Stripe's API `ui_mode` parameter (which moved to `embedded_page` in the 2026-03-25 Dahlia release). Keep this value as-is even when the underlying Stripe API call uses `embedded_page`.

---

## Dynamic Pricing

Two valid patterns. **Always compute the amount on the seller side.** Never accept an amount from the chat message, the UI, or the buyer's `CommitPayment`.

### A) Server-computed `amount_cents` (per request)

Use this when the price varies per request (size, plan, prompt length, promo code, etc.). The helper above already accepts an override:

```python
amount_cents = compute_price(plan, modifiers)  # seller-side only

checkout = create_embedded_checkout_session(
    user_address=user_address,
    chat_session_id=session_id,
    description=description,
    payment_request_id=uuid4().hex,
    amount_cents_override=amount_cents,
)
```

The helper bakes `amount_cents` into the `idempotency_key`, so re-attempting at a different price never collides with a prior session.

When dynamic pricing is in play, also assert the retrieved Checkout Session matches the seller-intended amount before fulfillment:

```python
result = verify_checkout_session_paid(tx_id)
if (
    not result.get("verified")
    or result.get("amount_total") != expected_cents
    or (result.get("currency") or "").lower() != expected_currency.lower()
):
    await ctx.send(sender, RejectPayment(reason="Stripe amount or currency mismatch."))
    return
```

### B) Pre-created Stripe Prices

Use this for a small fixed set of tiers. Create the `Price` in the Stripe Dashboard and set `STRIPE_PRICE_ID` — the helper switches to `line_items=[{"price": ..., "quantity": 1}]` automatically.

---

## Hard Rules

- Resolve package manager via the **Package Skill Precedence** block before any setup/run instructions.
- If a package skill is active, all setup/install/run commands must match that skill only.
- Default `Agent(...)` to `network="testnet"` for development (driven by `AGENT_NETWORK=testnet` in `.env.example`); switch to `"mainnet"` only when the user explicitly opts into a production deploy.
- On `network="testnet"`, always call `fund_agent_if_low(str(agent.wallet.address()))` immediately after `Agent(...)` so the wallet has enough testnet FET for Almanac registration. This is what suppresses the `[uagents.registration] I do not have enough funds to register on Almanac contract` warning loop. On mainnet, do NOT call it — the operator funds the wallet themselves.
- Use **Stripe Checkout Sessions** in `mode="payment"`. Never use the Charges API.
- The `transaction_id` on `CommitPayment` is the **Stripe Checkout Session ID** — never trust client-supplied amounts or status.
- Compute price on the **seller side**. Never derive `unit_amount` from the chat message, UI, or `CommitPayment`. For dynamic pricing, also verify `amount_total` + `currency` on retrieve.
- Always **verify server-side** via `stripe.checkout.Session.retrieve(...).payment_status == "paid"` before sending `CompletePayment`.
- Always reply to every `CommitPayment` with `CompletePayment` on success or `RejectPayment(reason=...)` on failure. (`CancelPayment` exists in the spec; `RejectPayment` is the canonical seller failure reply.)
- One pending `RequestPayment` per `(user_address, ctx.session)`. Do not spawn a new Checkout Session per chat message.
- Pass an `idempotency_key` when calling `stripe.checkout.Session.create`.
- Mark every processed `transaction_id` so duplicate `CommitPayment` deliveries are idempotent (no re-verification / no double charge).
- Track a fulfillment marker per `(user, session, transaction_id)` so duplicate `CommitPayment` can safely resume `run_paid_action(...)` if verification succeeded but fulfillment failed/interrupted.
- Bind Checkout Session ownership to the sender (`payment_request:by_checkout:<cs_id>.user_address`) and reject owner mismatches.
- For dynamic/fixed pricing, compare retrieved `amount_total` + `currency` against the seller-side expected values saved with the checkout reference before fulfillment.
- Register both protocols on the agent: `agent.include(chat_proto, publish_manifest=True)` and `agent.include(payment_proto, publish_manifest=True)`.
- Every handler starts with `log_inbound(...)`; every `ctx.send(...)` is preceded by `log_outbound(...)`; notable storage transitions use `log_state(...)`.
- Never log secret keys, full Stripe responses, `client_secret`, full `msg.metadata` dumps, or card data. Log only Checkout Session ID, `payment_method`, amount, currency, `payment_status`.

## Forbidden

- Do not output mixed package-manager commands in one solution (for example `uv add ...` plus `pip install ...`).
- Hardcoding `STRIPE_SECRET_KEY`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_PRICE_ID`, prices, currencies, or success URLs.
- Naming the local Stripe folder `stripe/` — it shadows the SDK. Use `stripe_payments/`.
- Calling the Stripe SDK from `chat_proto.py`, `payment_proto.py`, or `agent.py`. The SDK lives **only** in `stripe_payments/checkout.py`.
- Replying to `CommitPayment` with raw text as the payment-protocol reply. Always send `CompletePayment` / `RejectPayment` first; optional chat text may follow as a separate message.
- Fulfilling the paid action before `verify_checkout_session_paid(...)` returns `verified=True`.
- Subscriptions / recurring prices in `mode="payment"` (will fail). For subscriptions use `mode="subscription"`, and only after confirming the use case with the user.
- Sending raw card details to the agent — the user pays inside Stripe's embedded Checkout.

---

## Dependencies

Declare dependencies via the active package skill only:

- Always include `uagents` and `uagents-core`.
- Always include `stripe` for payment support.
- Always include `openai` because `run_paid_action` ships ASI:One-backed by default.
- Include `python-dotenv` only if env loading is used.
- Do not pin versions unless the project already pins others.

Do not create or mutate dependency manifests manually in this skill; defer manifest/lockfile behavior to the active package skill.

---

## Wrapping Patterns

- **Existing chat-only uAgent** → add `stripe_payments/checkout.py`, replace the chat protocol module with the `protocols/chat_proto.py` shown above (or merge the paid-action gate into the existing handler), add `protocols/payment_proto.py`, and register `payment_proto` in `agent.py`.
- **New agent from scratch** → create the four files above plus `.env`, then implement `_is_paid_request` and `run_paid_action` to suit the use case.
- **Agent with crypto payment already** → add Stripe alongside existing `Funds` entries in `accepted_funds`; branch in `on_commit` on `msg.funds.payment_method` and dispatch to the right verifier.

---

## Sample Chat (target UX)

```
User:  generate me an image of a sunset
Agent: [ChatAcknowledgement]
Agent: [RequestPayment with metadata.stripe -> embedded Checkout]
       "Once payment completes, I'll reply here with your result."
UI:    (Stripe embedded card form rendered from client_secret + publishable_key)
User:  pays with test card 4242 4242 4242 4242
UI:    sends CommitPayment(transaction_id=<checkout_session_id>, funds.payment_method="stripe")
Agent: [CompletePayment]
Agent: "Here's your image of a sunset: <url>"   # run_paid_action fired automatically
```

The chat handler decides *when* to call `request_payment_from_user(...)`. The payment handlers decide *how* to verify and then immediately call `run_paid_action(...)` so the buyer gets their result without sending another message. Keep these concerns in their own files.

---

## Testing Hints

- Run against a Stripe **sandbox / test mode** account before live keys.
- Use the Agentverse Agent Inspector link the agent prints on startup to drive the chat + Checkout end-to-end.
- Stripe test cards:
  - Success: `4242 4242 4242 4242` (any future expiry, any CVC, any ZIP).
  - Decline: `4000 0000 0000 0002` — confirms the `RejectPayment` path.
  - 3DS challenge: `4000 0027 6000 3184` — confirms the agent only sends `CompletePayment` once `payment_status == "paid"`.
- Confirm `payment_status == "paid"` on the retrieved Checkout Session before fulfillment. With dynamic pricing also assert `amount_total` and `currency`.
- Trigger duplicate `CommitPayment` to confirm idempotent replay logs `[state] duplicate_commit` + `[outbound] CompletePayment ... idempotent_replay=true` and does not duplicate fulfillment when already completed.
- Force a failure right after `CompletePayment` (e.g. temporary `run_paid_action` exception), then replay the same `CommitPayment`: verify it resumes fulfillment and logs `[state] post_payment_fulfilled ... replay=true`.
- Verify a `RejectPayment(reason=...)` reply when verification fails (bad session id, payment not yet completed, unsupported `funds.payment_method`, mismatched amount).

### Log Verification Checklist

Run the agent locally against Stripe test mode and confirm the CLI output shows the full trace:

- `[inbound] ChatMessage from <user>` at entry, then `[outbound] ChatAcknowledgement -> <user>` before the ack send.
- `[payment] stripe checkout created cs_id=cs_test_... amount_cents=... currency=... ui_mode=...` on success.
- `[outbound] RequestPayment -> <user> cs_id=cs_test_... amount_cents=...` immediately before the send.
- `[state] pending_request_saved user=<user> session=<session> cs_id=...` after persistence.
- `[inbound] CommitPayment from <user> tx_id=cs_test_... method=stripe` at entry.
- `[payment] stripe verify tx_id=cs_test_... verified=true status=paid amount_total=... currency=...`.
- `[state] payment_verified ...` then `[outbound] CompletePayment -> <user> tx_id=cs_test_...`.
- `[outbound] ChatMessage -> <user> paid_action_result` after the protocol reply (auto-fulfilled by `run_paid_action`).
- Duplicate `CommitPayment` path shows `[state] duplicate_commit` + `idempotent_replay=true`; if fulfillment had not completed earlier, replay should emit `[state] post_payment_fulfilled ... replay=true`.
- No `sk_...`, `pk_...`, `client_secret`, `cs_test_...` secrets beyond the ID, or full `msg.metadata` dumps appear in logs.

---

## Further Reading (optional)

These are not required to implement the agent — everything the agent needs is above. Consult only if a Stripe-specific edge case surfaces:

- Fetch.ai Stripe Horoscope walkthrough — `https://innovationlab.fetch.ai/resources/docs/examples/agent-transaction/stripe-horoscope-payment-protocol`
- Stripe Checkout Sessions API — `https://docs.stripe.com/api/checkout/sessions`
- Stripe test cards — `https://docs.stripe.com/testing`
