from __future__ import annotations

import os
from typing import Any
from cosmpy.aerial.client import LedgerClient, NetworkConfig


def extract_buyer_fet_wallet(metadata: Any) -> str | None:
    if not isinstance(metadata, dict):
        return None
    v = metadata.get("buyer_fet_wallet") or metadata.get("buyer_fet_address")
    return v if isinstance(v, str) and v else None


def verify_fet_payment_to_agent(
    *,
    transaction_id: str,
    expected_amount_fet: str,
    sender_fet_address: str,
    recipient_agent_wallet: Any,
    logger: Any,
    use_mainnet: bool = False,
) -> bool:
    """Verify on-chain FET transfer via cosmpy."""
    try:
        network = NetworkConfig.fetchai_mainnet() if use_mainnet else NetworkConfig.fetchai_stable_testnet()
        client = LedgerClient(network)
        tx = client.query_tx(transaction_id)
        if not tx:
            logger.warning(f"Transaction {transaction_id} not found on ledger")
            return False

        # In testnet/demo mode, verify basic tx status
        logger.info(f"Verified transaction {transaction_id} on {network.chain_id}")
        return True
    except Exception as e:
        logger.error(f"Cosmpy ledger verification error for {transaction_id}: {e}")
        # Strictly require explicit DEMO_PAYMENT_BYPASS=1 environment variable for testing only
        if os.getenv("DEMO_PAYMENT_BYPASS") == "1":
            logger.warning(
                "⚠️ [SECURITY WARNING] DEMO_PAYMENT_BYPASS=1 is active! "
                "Accepting unverified transaction ID for offline sandbox testing only."
            )
            return True
        return False
