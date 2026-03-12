"""
AgentPay - Compliance Validation
Checks counterparty whitelist and spend limits
"""
import os
import logging

logger = logging.getLogger(__name__)

# Mock approved counterparties (in production, load from database)
APPROVED_COUNTERPARTIES = {
    "0xAbC1234567890123456789012345678901234123": "Acme Supplies Ltd",
    "0xDef9876543210987654321098765432109876543": "Global Tech Inc",
    "0x1234567890123456789012345678901234567890": "Test Vendor Co",
}


def validate_invoice(invoice_data: dict) -> dict:
    """
    Validate invoice against compliance rules
    Returns: {status: "PASS" | "HOLD", reason: str}
    """
    dest_wallet = invoice_data.get("dest_wallet", "").lower()
    usdc_amount = float(invoice_data.get("usdc_amount", 0))
    vendor = invoice_data.get("vendor", "Unknown")
    
    spend_limit = float(os.getenv("AGENT_SPEND_LIMIT", 5000))
    
    logger.info(f"Validating invoice: {vendor} - {usdc_amount} USDC")
    
    # Check 1: Counterparty whitelist
    approved_wallets = {k.lower(): v for k, v in APPROVED_COUNTERPARTIES.items()}
    
    if dest_wallet not in approved_wallets:
        reason = f"Wallet {dest_wallet} not in approved counterparty list"
        logger.warning(f"HOLD: {reason}")
        return {"status": "HOLD", "reason": reason}
    
    logger.info(f"Counterparty: APPROVED ({approved_wallets[dest_wallet]})")
    
    # Check 2: Spend limit
    if usdc_amount > spend_limit:
        reason = f"Amount {usdc_amount} USDC exceeds spend limit of {spend_limit} USDC"
        logger.warning(f"HOLD: {reason}")
        return {"status": "HOLD", "reason": reason}
    
    logger.info(f"Spend: {usdc_amount} / {spend_limit} USDC — WITHIN LIMIT")
    logger.info("→ Status: PASS")
    
    return {"status": "PASS", "reason": "All compliance checks passed"}
