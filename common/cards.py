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


def build_strength_card(facts: dict[str, Any], strength: dict[str, Any]) -> dict[str, Any]:
    """Build a Review Card displaying Case Strength, Pecuniary Forum, and Evidence."""
    rows = [
        {"label": "Statutory Merit Score", "value": f"{strength['merit_score']}/100 ({strength['grade']})"},
        {"label": "Competent Forum", "value": strength["forum"]},
        {"label": "Pecuniary Rule", "value": strength["forum_rule"]},
        {"label": "Disputed Amount", "value": f"₹{facts.get('amount_inr', 'N/A')}"},
        {"label": "Core Violations", "value": " | ".join(strength["violations"][:2])},
        {"label": "Required Evidence", "value": " • ".join(strength["missing_evidence"])},
    ]
    return build_review_card(
        title=f"Legal Assessment & Case Merit — {facts.get('company', 'Enterprise')}",
        summary_rows=rows,
        approve_label="Draft Statutory Notice",
        reject_label="Edit Case Facts",
        approve_action="proceed_to_draft",
        reject_action="reject_or_edit",
    )


def build_reply_decision_card(
    case_id: str,
    company: str,
    classification: dict[str, Any],
    action_label: str,
    action_name: str,
) -> dict[str, Any]:
    """Build an interactive Review Card reflecting the agent's dynamic reply decision."""
    sentiment = classification.get("sentiment", "stalling").upper()
    reasoning = classification.get("reasoning", "")
    violation = classification.get("statutory_violation", "")

    rows = [
        {"label": "Case ID", "value": f"#{case_id}"},
        {"label": "Enterprise", "value": company},
        {"label": "Reply Classification", "value": sentiment},
        {"label": "Agent Decision", "value": classification.get("recommended_action", "").upper()},
        {"label": "Legal Analysis", "value": reasoning[:100]},
    ]
    if violation:
        rows.append({"label": "Statutory Breach", "value": violation})

    return build_review_card(
        title=f"Decision Loop: Corporate Response Evaluated — #{case_id}",
        summary_rows=rows,
        approve_label=action_label,
        reject_label="Edit Case / Cancel",
        approve_action=action_name,
        reject_action="reject_or_edit",
    )


def build_edaakhil_card(case_id: str, edaakhil_data: dict[str, Any]) -> dict[str, Any]:
    """Build an interactive Detail Card presenting the prepared e-Daakhil filing packet."""
    annexure_titles = " • ".join(a["title"] for a in edaakhil_data.get("annexures", []))
    rows = [
        {"label": "Case ID", "value": f"#{case_id}"},
        {"label": "Designated Forum", "value": edaakhil_data.get("forum", "District Commission")},
        {"label": "Petition Format", "value": "Section 35 Consumer Protection Act, 2019"},
        {"label": "Statutory Merit", "value": f"{edaakhil_data.get('merit_score', 92)}/100"},
        {"label": "Annexures Prepared", "value": annexure_titles},
        {"label": "Filing Portal", "value": "https://edaakhil.nic.in"},
    ]
    return build_detail_card(
        title=f"e-Daakhil Legal Petition Packet Ready — #{case_id}",
        summary_rows=rows,
        cta_label="View Full Petition Text",
        cta_action="view_edaakhil_petition",
    )


def build_health_card(components: list[dict[str, str]]) -> dict[str, Any]:
    """Build a Detail Card presenting system-wide health and reachability."""
    rows = [
        {"label": c["name"], "value": f"{c['status']} ({c['latency']})"}
        for c in components
    ]
    return build_detail_card(
        title="ReclaimAI Multi-Agent System Health",
        summary_rows=rows,
        cta_label="Refresh Diagnostics",
        cta_action="check_health",
    )


def parse_selection(text: str) -> dict[str, Any]:
    """Parse card selection from user or planner into a dictionary.

    Handles direct JSON from @mention interactions as well as embedded JSON payloads.
    """
    if not text:
        return {}

    # Strip mention prefixes like @reclaim-ai or @agent1q...
    cleaned = re.sub(r"^@[\w-]+\s*", "", text.strip())

    # Never treat explicit slash commands as card selection clicks
    if cleaned.startswith("/"):
        return {}

    # 1. Try direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    # 2. Try finding JSON inside markdown code blocks or brackets
    json_match = re.search(r"\{[^{}]*\}", cleaned, re.DOTALL)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # 3. Fallback: only match explicit confirmation / rejection phrases
    extracted: dict[str, Any] = {"raw": text}
    lower = cleaned.lower()
    if ("approve" in lower or "confirm" in lower) and not ("not approve" in lower or "don't approve" in lower):
        extracted["action"] = "approve_dispatch"
    elif lower in ("reject", "cancel", "edit", "no", "reject & edit", "cancel notice"):
        extracted["action"] = "reject_or_edit"

    return extracted
