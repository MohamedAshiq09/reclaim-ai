from __future__ import annotations

from typing import Any
from uagents import Context


def truncate(text: str | None, max_len: int = 120) -> str:
    if not text:
        return ""
    text_clean = str(text).replace("\n", " ").strip()
    if len(text_clean) > max_len:
        return text_clean[:max_len] + "..."
    return text_clean


def log_inbound(ctx: Context, msg_type: str, sender: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    ctx.logger.info(f"[inbound] {msg_type} from {sender}{suffix}")


def log_outbound(ctx: Context, msg_type: str, recipient: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    ctx.logger.info(f"[outbound] {msg_type} -> {recipient}{suffix}")


def log_state(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    ctx.logger.info(f"[state] {event}{suffix}")


def log_payment(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    ctx.logger.info(f"[payment] {event}{suffix}")


def log_error(ctx: Context, error: Any, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    ctx.logger.error(f"[error] {error}{suffix}")
