from __future__ import annotations

import json
import re
from typing import Any, Optional
from openai import OpenAI
from common.config import ASI_ONE_API_KEY, ASI_ONE_BASE_URL, ASI_ONE_MODEL


def get_llm_client() -> Optional[OpenAI]:
    if not ASI_ONE_API_KEY:
        return None
    return OpenAI(
        api_key=ASI_ONE_API_KEY,
        base_url=ASI_ONE_BASE_URL,
    )


def classify_intent_and_extract(user_text: str) -> dict[str, Any]:
    """Extract case facts and classify consumer dispute category using ASI:One."""
    client = get_llm_client()
    default_res = _heuristic_extraction(user_text)

    if not client:
        return default_res

    prompt = f"""You are ReclaimAI's intent analyzer for Indian consumer disputes.
Analyze the user complaint text and return a JSON object with these exact keys:
- "category": one of ["ecommerce", "airline", "bank", "telecom", "insurance", "other"]
- "company": extracted company name (e.g. "Flipkart", "Indigo", "HDFC", "Airtel")
- "order_ref": extracted order ID, PNR, transaction reference or null
- "amount_inr": extracted numeric amount in INR or null
- "order_date": extracted date or null
- "issue_summary": concise summary of what went wrong
- "desired_outcome": e.g. "Full refund of amount paid"

User text: {user_text}

Respond ONLY with valid JSON.
"""
    try:
        response = client.chat.completions.create(
            model=ASI_ONE_MODEL,
            messages=[
                {"role": "system", "content": "You are a precise JSON extractor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=500,
        )
        content = response.choices[0].message.content or ""
        # Find JSON block
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            # Merge with default_res to guarantee all required keys exist
            for k, v in default_res.items():
                if k not in data or data[k] is None:
                    data[k] = v
            return data
    except Exception as e:
        print(f"[llm] Intent classification error (falling back to heuristics): {e}")

    return default_res


def _heuristic_extraction(text: str) -> dict[str, Any]:
    text_lower = text.lower()

    # Category detection
    if any(k in text_lower for k in ["flight", "airline", "indigo", "air india", "spicejet", "pnr", "airport"]):
        category = "airline"
    elif any(k in text_lower for k in ["bank", "charge", "upi", "hdfc", "sbi", "icici", "debit", "credit card", "atm"]):
        category = "bank"
    elif any(k in text_lower for k in ["recharge", "sim", "telecom", "airtel", "jio", "vi", "vodafone"]):
        category = "telecom"
    elif any(k in text_lower for k in ["insurance", "claim", "policy", "lic"]):
        category = "insurance"
    else:
        category = "ecommerce"

    # Company detection
    company = "Merchant / Service Provider"
    for brand in ["flipkart", "amazon", "myntra", "meesho", "zomato", "swiggy", "indigo", "air india", "spicejet", "hdfc", "sbi", "icici", "airtel", "jio"]:
        if brand in text_lower:
            company = brand.capitalize()
            if brand == "air india":
                company = "Air India"
            elif brand in ("hdfc", "sbi", "icici"):
                company = brand.upper()
            break

    # Amount extraction
    amount = None
    amt_match = re.search(r"(?:rs\.?|inr|₹)\s*([\d,]+)", text, re.IGNORECASE)
    if amt_match:
        try:
            amount = float(amt_match.group(1).replace(",", ""))
        except Exception:
            pass

    # Order ref
    order_ref = None
    ref_match = re.search(r"(?:order|od|pnr|txn|ref)[:#\s]*([a-zA-Z0-9_\-]+)", text, re.IGNORECASE)
    if ref_match:
        order_ref = ref_match.group(1).strip()

    return {
        "category": category,
        "company": company,
        "order_ref": order_ref,
        "amount_inr": amount,
        "order_date": None,
        "issue_summary": text[:200].strip(),
        "desired_outcome": "Immediate full refund of funds and official redressal",
    }


def generate_complaint_draft(
    facts: dict[str, Any],
    research: dict[str, Any],
    tier: int = 1,
    feedback: str | None = None,
) -> dict[str, str]:
    """Generate formal legal notice citing Indian consumer laws."""
    client = get_llm_client()
    company = facts.get("company", "Company")
    order_ref = facts.get("order_ref") or "REF-PENDING"
    amount = facts.get("amount_inr") or "Applicable Amount"
    issue = facts.get("issue_summary", "Unfair trade practice and non-delivery of service")
    user_name = facts.get("user_name", "Aggrieved Consumer")
    user_email = facts.get("user_email", "")

    rights_summary = research.get("rights_summary", "")
    citations_text = "\n".join(
        [f"- {c.get('title')}: {c.get('note')} (Source: {c.get('url')})" for c in research.get("citations", [])]
    )

    if tier == 1:
        subject = f"FORMAL GRIEVANCE NOTICE: Deficiency in Service / Unfair Trade Practice - Order Ref #{order_ref} - {company}"
    else:
        subject = f"ESCALATION TIER-2: Unresolved Consumer Complaint against {company} [Ref: #{order_ref}]"

    if client:
        prompt = f"""You are an expert Indian Consumer Law Drafter.
Write a firm, professional, legally grounded grievance letter in English.
Details:
- Recipient: Grievance Officer, {company} (Tier {tier})
- Complainant Name: {user_name} ({user_email})
- Company: {company}
- Order / Case Ref: {order_ref}
- Disputed Amount: INR {amount}
- Issue Details: {issue}
- Statutory Rights & Legal Grounds: {rights_summary}
- Legal Citations to cite:
{citations_text}
- User Feedback: {feedback or 'None'}

Notice Requirements:
1. Clearly state the factual sequence of events.
2. Cite the Consumer Protection Act, 2019 and relevant statutory rules.
3. State the mandatory statutory deadline for grievance redressal (48h acknowledgment, 30 days resolution).
4. Demand the desired outcome (full refund of INR {amount}).
5. Give notice that failure to resolve within the statutory period will compel escalation to the National Consumer Helpline (NCH), e-Daakhil Consumer Commission, and regulatory authorities with claims for damages and statutory compensation.
6. Include the mandatory statutory disclaimer: 'This communication is issued by the consumer exercising statutory rights under the Consumer Protection Act, 2019.'

Output ONLY valid JSON with keys "subject" and "body".
"""
        try:
            response = client.chat.completions.create(
                model=ASI_ONE_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional legal drafter specializing in Indian consumer law."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=900,
            )
            content = response.choices[0].message.content or ""
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                if "subject" in data and "body" in data:
                    return {"subject": data["subject"], "body": data["body"]}
        except Exception as e:
            print(f"[llm] Draft generation error: {e}")

    # Deterministic fallback draft
    body = f"""To:
The Grievance Officer, {company}

SUBJECT: {subject}

Dear Sir/Madam,

I am writing this formal grievance notice regarding deficiency of service and unfair trade practices in connection with my transaction with {company}.

TRANSACTION DETAILS:
- Complainant: {user_name}
- Registered Email: {user_email}
- Order / Transaction Reference: {order_ref}
- Disputed Amount: INR {amount}

FACTS OF THE GRIEVANCE:
{issue}

STATUTORY RIGHTS & LEGAL CITATIONS:
{rights_summary}

Applicable Provisions:
{citations_text}

DEMAND & RELIEF SOUGHT:
In accordance with Rule 5(4) of the Consumer Protection (E-Commerce) Rules, 2020 and the Consumer Protection Act, 2019, your entity is mandated to acknowledge this grievance within forty-eight (48) hours and redress the complaint within one month from the date of receipt.

I hereby demand:
1. Immediate reversal and full refund of INR {amount} to my original payment source.
2. Written confirmation of grievance resolution.

NOTICE OF STATUTORY ESCALATION:
Please take note that in the event of your failure to redress this grievance within the statutory timeline, I shall proceed without further notice to escalate this matter to the National Consumer Helpline (NCH / consumerhelpline.gov.in), file an online petition before the Consumer Disputes Redressal Commission via the e-Daakhil portal (edaakhil.nic.in), and report the non-compliance to the Central Consumer Protection Authority (CCPA) for statutory penalties.

Yours sincerely,
{user_name}
(Complainant)

DISCLAIMER: This notice is issued under the statutory framework of the Consumer Protection Act, 2019 and relevant sector regulations.
"""
    return {"subject": subject, "body": body}
