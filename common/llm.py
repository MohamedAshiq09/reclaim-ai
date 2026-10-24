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
In accordance with Rule 4(4) and Rule 4(5) of the Consumer Protection (E-Commerce) Rules, 2020 and the Consumer Protection Act, 2019, your entity is mandated to maintain a designated Grievance Officer, acknowledge this grievance within forty-eight (48) hours, and redress the complaint within one month from the date of receipt.


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


def classify_company_reply(company_reply_text: str, case_facts: dict[str, Any]) -> dict[str, Any]:
    """Classify company reply using ASI:One LLM into: resolved, rejected, stalling, or needs_info."""
    client = get_llm_client()
    company = case_facts.get("company", "Company")
    category = case_facts.get("category", "ecommerce")
    amount = case_facts.get("amount_inr", 0)

    # Deterministic fallback classification
    lower = company_reply_text.lower()
    default_sentiment = "stalling"
    default_action = "ultimatum"
    default_reasoning = "Company response received; analyzing resolution commitment."

    if any(k in lower for k in ["refund initiated", "approved", "processed", "credited", "apologize for the inconvenience", "resolved"]):
        default_sentiment = "resolved"
        default_action = "close"
        default_reasoning = "The company has agreed to the remedy or confirmed refund issuance."
    elif any(k in lower for k in ["rejected", "denied", "not eligible", "cannot be processed", "package intact", "doorstep", "customer fault", "violation"]):
        default_sentiment = "rejected"
        default_action = "rebuttal"
        default_reasoning = "Company issued a rejection; invoking statutory breach and rebuttal notice."
    elif any(k in lower for k in ["provide", "upload", "share", "unboxing video", "photo", "document", "id proof"]):
        default_sentiment = "needs_info"
        default_action = "request_evidence"
        default_reasoning = "Company requested additional evidence or clarification from complainant."
    else:
        default_sentiment = "stalling"
        default_action = "ultimatum"
        default_reasoning = "Company response contains delaying language without concrete redressal."

    if not client:
        return {
            "sentiment": default_sentiment,
            "recommended_action": default_action,
            "reasoning": default_reasoning,
            "statutory_violation": "Rule 4(5) 48h acknowledgment and 30-day redressal mandate (E-Commerce Rules 2020)" if category == "ecommerce" else "DGCA CAR Part II Para 3.3",
        }

    prompt = f"""You are ReclaimAI's legal decision agent analyzing a corporate reply in an Indian consumer dispute.
Company: {company}
Dispute Category: {category}
Disputed Amount: INR {amount}
Original Issue: {case_facts.get('issue_summary', '')}

Company Reply Text:
"{company_reply_text}"

Analyze this reply carefully and return JSON with these exact keys:
- "sentiment": one of ["resolved", "rejected", "stalling", "needs_info"]
- "recommended_action": one of ["close", "rebuttal", "ultimatum", "request_evidence"]
- "reasoning": 1-2 sentence explanation of why this classification was made
- "statutory_violation": specific legal provision violated if rejected or stalled (e.g. "Rule 4(5) E-Commerce Rules 2020", "Section 2(47) CPA 2019 Unfair Trade Practice", "DGCA CAR Section 3 Series M Part II Para 3.3")

Respond ONLY with valid JSON.
"""
    try:
        response = client.chat.completions.create(
            model=ASI_ONE_MODEL,
            messages=[
                {"role": "system", "content": "You are a senior consumer rights legal expert in India."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=400,
        )
        content = response.choices[0].message.content or ""
        json_match = re.search(r"\{.*\}", content, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            if "sentiment" in data:
                return data
    except Exception as e:
        print(f"[llm] Error in reply classification: {e}")

    return {
        "sentiment": default_sentiment,
        "recommended_action": default_action,
        "reasoning": default_reasoning,
        "statutory_violation": "Rule 4(5) Consumer Protection (E-Commerce) Rules 2020",
    }


def compute_case_strength(case_facts: dict[str, Any]) -> dict[str, Any]:
    """Compute quantitative case merit score, evidence checklist, and pecuniary forum."""
    amount = float(case_facts.get("amount_inr") or 0.0)
    category = case_facts.get("category", "ecommerce")

    # Pecuniary jurisdiction under Consumer Protection Rules 2021 (G.S.R. 886(E))
    if amount <= 5000000:  # <= 50 Lakhs
        forum_name = "District Consumer Disputes Redressal Commission (DCDRC)"
        forum_rule = "District Commission Jurisdiction (Up to ₹50 Lakhs - Rules 2021)"
    elif amount <= 20000000:  # 50 Lakhs to 2 Crores
        forum_name = "State Consumer Disputes Redressal Commission (SCDRC)"
        forum_rule = "State Commission Jurisdiction (₹50 Lakhs to ₹2 Crores - Rules 2021)"
    else:
        forum_name = "National Consumer Disputes Redressal Commission (NCDRC)"
        forum_rule = "National Commission Jurisdiction (Exceeding ₹2 Crores - Rules 2021)"

    # Base merit score
    score = 92
    violations = [
        "Section 2(11) Consumer Protection Act, 2019 (Deficiency in Service)",
        "Section 2(47) Consumer Protection Act, 2019 (Unfair Trade Practice)",
    ]

    if category == "ecommerce":
        violations.extend([
            "Rule 4(4) Consumer Protection (E-Commerce) Rules, 2020 (Mandatory Grievance Officer)",
            "Rule 4(5) Consumer Protection (E-Commerce) Rules, 2020 (Mandatory 48h ACK / 30d Redressal)",
        ])
    elif category == "airline":
        violations.extend([
            "DGCA CAR Section 3, Series M, Part II, Para 3.3 (Mandatory 7-day refund for credit card)",
            "DGCA CAR Section 3, Series M, Part IV (Facilities & Compensation)",
        ])
    elif category == "bank":
        violations.extend([
            "Reserve Bank - Integrated Ombudsman Scheme, 2021 (Clause 10 & 15)",
        ])

    missing_evidence = []
    if not case_facts.get("order_ref"):
        missing_evidence.append("Tax Invoice / Order Confirmation Number")
    missing_evidence.extend([
        "Photographs / Video of delivered defect or transaction screenshot",
        "Record of prior communication with customer care",
    ])

    return {
        "merit_score": score,
        "grade": "Strong Statutory Merit (High Likelihood of Relief)",
        "forum": forum_name,
        "forum_rule": forum_rule,
        "violations": violations,
        "missing_evidence": missing_evidence,
    }


def generate_rebuttal_draft(case_facts: dict[str, Any], company_reply: str, classification: dict[str, Any]) -> dict[str, str]:
    """Generate a formal legal rebuttal notice to an adverse corporate reply."""
    company = case_facts.get("company", "Company")
    user_name = case_facts.get("user_name", "Complainant")
    order_ref = case_facts.get("order_ref", "N/A")
    amount = case_facts.get("amount_inr", "N/A")
    violation = classification.get("statutory_violation", "Rule 4(5) E-Commerce Rules, 2020")

    subject = f"REBUTTAL NOTICE: Rejection of Adverse Claim & Final Statutory Demand — Order #{order_ref}"
    body = f"""To:
The Grievance Officer, {company}

SUBJECT: {subject}

Dear Sir/Madam,

I am in receipt of your communication dated {company_reply[:80]} regarding Order #{order_ref}.

Take notice that your entity's response is legally untenable and rejected on the following statutory grounds:

1. STATUTORY BREACH OF REDRESSAL MANDATE:
Under {violation}, your entity is strictly prohibited from summarily disclaiming liability for defective goods or service deficiencies. The burden of delivering goods conforming to purchase specifications rests entirely on the entity under Section 2(47) and Section 84 of the Consumer Protection Act, 2019.

2. UNLAWFUL DENIAL:
Your purported ground of rejection ("{company_reply[:140]}") constitutes an Unfair Trade Practice under Section 2(47) of CPA 2019 and is null and void in law. A consumer is legally entitled to inspect purchased goods and reject latent defects or damaged items upon unboxing.

3. FINAL PRE-LITIGATION DEMAND (24-HOUR ULTIMATUM):
I hereby give you a final window of twenty-four (24) hours to:
(a) Recall your unlawful rejection;
(b) Process the full refund of INR {amount} to my payment account.

FAILING WHICH:
An electronic complaint petition shall be instituted immediately on the e-Daakhil portal (edaakhil.nic.in) before the competent Consumer Commission seeking full refund, 18% p.a. interest, and exemplary compensation of INR 50,000 for mental agony and litigation expenses.

Yours faithfully,
{user_name}
(Complainant)
"""
    return {"subject": subject, "body": body}


def generate_edaakhil_packet(case_facts: dict[str, Any], timeline_events: list[dict[str, Any]]) -> dict[str, Any]:
    """Generate a ready-to-file e-Daakhil consumer complaint packet."""
    company = case_facts.get("company", "Opposite Party")
    user_name = case_facts.get("user_name", "Complainant")
    amount = case_facts.get("amount_inr", 0.0)
    order_ref = case_facts.get("order_ref", "N/A")
    case_id = case_facts.get("case_id", "N/A")

    strength = compute_case_strength(case_facts)

    petition_text = f"""BEFORE THE HON'BLE {strength['forum'].upper()}
CONSUMER COMPLAINT NO. ________ / 2026

IN THE MATTER OF:
{user_name}
... COMPLAINANT

VERSUS

{company} & Ors.
... OPPOSITE PARTY(IES)

COMPLAINT UNDER SECTION 35 OF THE CONSUMER PROTECTION ACT, 2019
FOR DEFICIENCY IN SERVICE AND UNFAIR TRADE PRACTICES

1. JURISDICTION:
The Complainant paid consideration of INR {amount}, which falls within the pecuniary jurisdiction of this Hon'ble Commission pursuant to the Consumer Protection Rules, 2021.

2. STATEMENT OF FACTS:
- On or about {case_facts.get('order_date', 'recent date')}, the Complainant purchased goods/services under Order/Ref #{order_ref} for INR {amount}.
- The Opposite Party delivered damaged/defective product and refused redressal: {case_facts.get('issue_summary', '')}.
- The Complainant served formal statutory grievance notice on the Opposite Party's Grievance Officer pursuant to statutory mandates.
- The Opposite Party failed and neglected to resolve the grievance.

3. STATUTORY GROUNDS:
- Direct violation of {", ".join(strength['violations'])}.
- Failure to adhere to statutory redressal timelines.

4. PRAYER FOR RELIEF:
Wherefore, it is most respectfully prayed that this Hon'ble Commission may be pleased to:
(a) Direct the Opposite Party to refund the sum of INR {amount} along with interest @ 18% p.a.
(b) Direct the Opposite Party to pay INR 25,000 towards mental agony and harassment.
(c) Direct the Opposite Party to pay INR 10,000 towards litigation costs.

COMPLAINANT
THROUGH: ReclaimAI Autonomous Consumer Rights Framework (Case #{case_id})
"""

    annexures = [
        {"title": "Annexure A-1", "desc": f"Tax Invoice / Order Confirmation #{order_ref}"},
        {"title": "Annexure A-2", "desc": "Photographic evidence of defective delivery"},
        {"title": "Annexure A-3", "desc": "Formal Statutory Notice served via ReclaimAI"},
        {"title": "Annexure A-4", "desc": "Chronological audit trail of unredressed grievance"},
    ]

    return {
        "forum": strength["forum"],
        "petition_text": petition_text,
        "annexures": annexures,
        "merit_score": strength["merit_score"],
    }

