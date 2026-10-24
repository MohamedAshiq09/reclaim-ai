from __future__ import annotations

from typing import Any
from uagents import Context


import os
from datetime import datetime, timezone
from pathlib import Path

LIVE_LOG_FILE = Path("logs/live.log")
LIVE_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def append_to_live_log(level: str, tag: str, message: str) -> None:
    """Append structured message directly to logs/live.log for real-time audit."""
    try:
        now_str = datetime.now(timezone.utc).isoformat()
        with open(LIVE_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{now_str}] [{level}] [{tag}] {message}\n")
    except Exception:
        pass


def truncate(text: str | None, max_len: int = 120) -> str:
    if not text:
        return ""
    text_clean = str(text).replace("\n", " ").strip()
    if len(text_clean) > max_len:
        return text_clean[:max_len] + "..."
    return text_clean


def log_inbound(ctx: Context, msg_type: str, sender: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    line = f"{msg_type} from {sender}{suffix}"
    ctx.logger.info(f"[inbound] {line}")
    append_to_live_log("INFO", "inbound", line)


def log_outbound(ctx: Context, msg_type: str, recipient: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    line = f"{msg_type} -> {recipient}{suffix}"
    ctx.logger.info(f"[outbound] {line}")
    append_to_live_log("INFO", "outbound", line)


def log_state(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    line = f"{event}{suffix}"
    ctx.logger.info(f"[state] {line}")
    append_to_live_log("INFO", "state", line)


def log_payment(ctx: Context, event: str, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    line = f"{event}{suffix}"
    ctx.logger.info(f"[payment] {line}")
    append_to_live_log("INFO", "payment", line)


def log_error(ctx: Context, error: Any, details: str | None = None) -> None:
    suffix = f" {truncate(details)}" if details else ""
    line = f"{error}{suffix}"
    ctx.logger.error(f"[error] {line}")
    append_to_live_log("ERROR", "error", line)

