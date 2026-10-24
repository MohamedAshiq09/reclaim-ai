from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from uagents_core.contrib.protocols.chat import (
    ChatMessage,
    MetadataContent,
    TextContent,
)


def card_message(
    narration: str,
    card_kind: str,
    payload: dict[str, Any],
    is_terminal: bool = False,
    preferred_drawer_width_px: int = 540,
) -> ChatMessage:
    """Build a ChatMessage that renders an ASI:One Interactive Card."""
    metadata = {
        "card_protocol_version": "1",
        "card_kind": card_kind,
        "card_payload": json.dumps(payload),
        "is_terminal": "true" if is_terminal else "false",
        "preferred_drawer_width_px": str(preferred_drawer_width_px),
    }
    if not is_terminal:
        metadata["requires_card_interaction"] = "true"

    return ChatMessage(
        timestamp=datetime.now(timezone.utc),
        msg_id=uuid4(),
        content=[
            TextContent(type="text", text=narration),
            MetadataContent(type="metadata", metadata=metadata),
        ],
    )


def build_form_card(
    title: str,
    fields: list[dict[str, Any]],
    submit_label: str = "Submit Grievance Details",
    action: str = "submit_case_facts",
) -> dict[str, Any]:
    """Build a predefined 'form' card payload."""
    return {
        "title": title,
        "fields": fields,
        "submit_cta": {
            "label": submit_label,
            "selection": {"action": action},
        },
    }


def build_detail_card(
    title: str,
    summary_rows: list[dict[str, str]],
    cta_label: str = "Proceed to Formal Complaint Draft",
    cta_action: str = "proceed_to_draft",
    hero_image: str | None = None,
) -> dict[str, Any]:
    """Build a predefined 'detail' card payload."""
    payload: dict[str, Any] = {
        "title": title,
        "summary_rows": summary_rows,
        "ctas": [
            {
                "label": cta_label,
                "selection": {"action": cta_action},
                "primary": True,
            }
        ],
    }
    if hero_image:
        payload["hero_image"] = hero_image
    return payload


def build_review_card(
    title: str,
    summary_rows: list[dict[str, str]],
    approve_label: str = "Approve & Dispatch Notice",
    reject_label: str = "Edit Details / Cancel",
    approve_action: str = "approve_dispatch",
    reject_action: str = "reject_or_edit",
) -> dict[str, Any]:
    """Build a predefined 'review' card payload."""
    return {
        "title": title,
        "summary_rows": summary_rows,
        "approve_cta": {
            "label": approve_label,
            "selection": {"action": approve_action},
            "primary": True,
        },
        "reject_cta": {
            "label": reject_label,
            "selection": {"action": reject_action},
        },
    }


def build_carousel_card(
    title: str,
    subtitle: str,
    items: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a predefined 'carousel' card payload for case timeline / options."""
    return {
        "title": title,
        "subtitle": subtitle,
        "items": items,
    }


def parse_selection(text: str) -> dict[str, Any]:
    """Parse card selection from user or planner into a dictionary.

    Handles direct JSON from @mention interactions as well as heuristic
    key-value extraction from planner prose.
    """
    if not text:
        return {}

    # 1. Try direct JSON parsing
    try:
        data = json.loads(text)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # 2. Try finding JSON inside markdown code blocks or brackets
    json_match = re.search(r"\{.*\}", text, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # 3. Fallback: extract common key-value pairs from text
    extracted: dict[str, Any] = {"raw": text}
    lower = text.lower()
    if "approve" in lower or "confirm" in lower:
        extracted["action"] = "approve_dispatch"
    elif "reject" in lower or "cancel" in lower or "edit" in lower:
        extracted["action"] = "reject_or_edit"
    elif "proceed" in lower or "continue" in lower or "draft" in lower:
        extracted["action"] = "proceed_to_draft"
    elif "submit" in lower:
        extracted["action"] = "submit_case_facts"

    # Try extracting named fields if present in text
    for field in ["company", "order_ref", "amount_inr", "order_date", "user_email", "user_name"]:
        m = re.search(rf"{field}[:=]\s*([^\s,;]+)", text, re.IGNORECASE)
        if m:
            extracted[field] = m.group(1).strip()

    return extracted
