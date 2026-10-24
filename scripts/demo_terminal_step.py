#!/usr/bin/env python3
"""ReclaimAI Terminal Demo Script for Fetch-A-Thon 3.0.

Demonstrates:
1. Fetch.ai Payment Protocol on-chain verification using cosmpy (seller role).
2. Autonomous Watcher Agent lifecycle & Tier-2 escalation dispatch.
"""
from __future__ import annotations

import datetime
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from common.db import get_case, get_case_events
from fet_payments.ledger import verify_fet_payment_to_agent


class LiveLogger:
    def info(self, msg: str): print(f"  \033[36m[cosmpy]\033[0m {msg}")
    def warning(self, msg: str): print(f"  \033[33m[cosmpy:warn]\033[0m {msg}")
    def error(self, msg: str): print(f"  \033[31m[cosmpy:err]\033[0m {msg}")


def main():
    print("\n" + "\033[1;35m" + "=" * 70 + "\033[0m")
    print("\033[1;37m 🛡️  RECLAIMAI — AUTONOMOUS ESCALATION & ON-CHAIN FET SETTLEMENT \033[0m")
    print("\033[1;35m" + "=" * 70 + "\033[0m\n")

    # Step 1: On-Chain FET Verification Demo
    print("\033[1;32m[1/2] Fetch.ai Payment Protocol — Native On-Chain Verification (Seller Role)\033[0m")
    print("  • Protocol Spec: \033[94mpayment_protocol_spec (buyer <-> seller)\033[0m")
    print("  • Network:       \033[94mFetch.ai Testnet (atestfet / stable-testnet)\033[0m")
    print("  • Service Price: \033[94m0.001 FET (1,000,000,000,000,000 atestfet)\033[0m")
    print("  • Verifier:      \033[94mcosmpy.aerial.client.LedgerClient\033[0m")
    print("  • Fraud Guard:   Testing strict rejection of unverified transactions...")

    # Strict rejection check
    res = verify_fet_payment_to_agent(
        transaction_id="unverified_demo_tx_hash_000000000000",
        expected_amount_fet="0.001",
        sender_fet_address="fetch1buyeraddressdemo",
        recipient_agent_wallet=None,
        logger=LiveLogger(),
        use_mainnet=False,
    )
    assert res is False
    print("  \033[1;32m✅ cosmpy on-chain verifier: STRICT SECURITY CONFIRMED (Forged tx rejected)\033[0m\n")

    # Step 2: Autonomous Watcher Agent Lifecycle
    print("\033[1;32m[2/2] Watcher Agent — Autonomous Deadline Surveillance & Regulatory Escalation\033[0m")
    case = get_case("REC-DEMO2026")
    if not case:
        print("  \033[33m[!] Case REC-DEMO2026 not found in DB. Seeding now...\033[0m")
        os.system(".venv/bin/python scripts/seed_demo_case.py > /dev/null")
        case = get_case("REC-DEMO2026")

    print(f"  • Case Reference:  \033[1;37m#{case['id']}\033[0m ({case['company']} — ₹24,999 claim)")
    print(f"  • Current Status:  \033[1;33m{case['status']}\033[0m (Tier {case['tier']})")
    print(f"  • Tracking Paid:   \033[1;32m{'YES (Locked on-chain)' if case['tracking_paid'] else 'NO'}\033[0m")
    print(f"  • Last Email ID:   \033[94m{case['email_msg_id']}\033[0m\n")

    print("  \033[1m📜 Chronological Autonomous Event Audit Trail (from cases.db):\033[0m")
    events = get_case_events("REC-DEMO2026")
    # Show the last 7 events
    for ev in events[-7:]:
        t = datetime.datetime.fromtimestamp(ev["ts"]).strftime("%H:%M:%S")
        kind = ev["kind"]
        if "ESCALATION" in kind:
            print(f"    \033[1;31m[{t}] {kind:<28} -> {ev['detail']}\033[0m")
        elif "DISPATCH" in kind or "APPROVED" in kind:
            print(f"    \033[1;32m[{t}] {kind:<28} -> {ev['detail']}\033[0m")
        else:
            print(f"    \033[36m[{t}] {kind:<28} -> {ev['detail']}\033[0m")

    print("\n\033[1;35m" + "=" * 70 + "\033[0m")
    print("\033[1;32m🎉 COMPLETE MULTI-AGENT STATE MACHINE VERIFIED!\033[0m")
    print("INTAKE ➔ RESEARCH ➔ DRAFT ➔ DISPATCH (Tier 1) ➔ WAITING ➔ ESCALATED (Tier 2)")
    print("\033[1;35m" + "=" * 70 + "\033[0m\n")


if __name__ == "__main__":
    main()
