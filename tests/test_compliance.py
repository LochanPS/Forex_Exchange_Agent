"""
Unit tests for compliance validation
"""
import os
import pytest
from compliance import validate_invoice


def test_approved_counterparty_within_limit():
    """Test invoice that passes all checks"""
    os.environ["AGENT_SPEND_LIMIT"] = "5000"
    
    invoice = {
        "vendor": "Acme Supplies Ltd",
        "usdc_amount": 1200.00,
        "dest_wallet": "0xAbC1234567890123456789012345678901234123"
    }
    
    result = validate_invoice(invoice)
    assert result["status"] == "PASS"


def test_unapproved_counterparty():
    """Test invoice with unapproved wallet"""
    invoice = {
        "vendor": "Unknown Vendor",
        "usdc_amount": 500.00,
        "dest_wallet": "0x0000000000000000000000000000000000000000"
    }
    
    result = validate_invoice(invoice)
    assert result["status"] == "HOLD"
    assert "not in approved" in result["reason"]


def test_exceeds_spend_limit():
    """Test invoice that exceeds spend limit"""
    os.environ["AGENT_SPEND_LIMIT"] = "5000"
    
    invoice = {
        "vendor": "Acme Supplies Ltd",
        "usdc_amount": 8500.00,
        "dest_wallet": "0xAbC1234567890123456789012345678901234123"
    }
    
    result = validate_invoice(invoice)
    assert result["status"] == "HOLD"
    assert "exceeds spend limit" in result["reason"]
