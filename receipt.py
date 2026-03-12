"""
AgentPay - Receipt Generation
Creates JSON and HTML receipts for settled payments
"""
import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def generate_receipt(invoice_data: dict, payment_result: dict, filename: str):
    """
    Generate payment receipt in JSON and HTML formats
    """
    timestamp = datetime.now().isoformat()
    
    receipt_data = {
        "timestamp": timestamp,
        "invoice": invoice_data,
        "payment": payment_result,
        "status": "SETTLED"
    }
    
    # Save JSON receipt
    json_path = f"settled/receipt_{filename}.json"
    with open(json_path, "w") as f:
        json.dump(receipt_data, f, indent=2)
    
    logger.info(f"Saved: {json_path}")
    
    # Generate HTML receipt
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Payment Receipt - {invoice_data.get('invoice_id', 'N/A')}</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #0052FF; }}
        .section {{ margin: 20px 0; padding: 15px; background: #f5f5f5; border-radius: 5px; }}
        .label {{ font-weight: bold; }}
        .success {{ color: #28a745; }}
        a {{ color: #0052FF; }}
    </style>
</head>
<body>
    <h1>⚡ AgentPay - Payment Receipt</h1>
    
    <div class="section">
        <h2>Invoice Details</h2>
        <p><span class="label">Vendor:</span> {invoice_data.get('vendor', 'N/A')}</p>
        <p><span class="label">Invoice ID:</span> {invoice_data.get('invoice_id', 'N/A')}</p>
        <p><span class="label">Amount:</span> {invoice_data.get('usdc_amount', 0)} USDC</p>
        <p><span class="label">Due Date:</span> {invoice_data.get('due_date', 'N/A')}</p>
    </div>
    
    <div class="section">
        <h2>Payment Details</h2>
        <p><span class="label">Status:</span> <span class="success">CONFIRMED</span></p>
        <p><span class="label">Transaction Hash:</span> {payment_result.get('tx_hash', 'N/A')}</p>
        <p><span class="label">Block Number:</span> {payment_result.get('block_number', 'N/A')}</p>
        <p><span class="label">Destination:</span> {invoice_data.get('dest_wallet', 'N/A')}</p>
        <p><span class="label">Timestamp:</span> {timestamp}</p>
    </div>
    
    <div class="section">
        <h2>Verification</h2>
        <p><a href="{payment_result.get('explorer_url', '#')}" target="_blank">View on Block Explorer →</a></p>
    </div>
</body>
</html>"""
    
    html_path = f"settled/receipt_{filename}.html"
    with open(html_path, "w") as f:
        f.write(html_content)
    
    logger.info(f"HTML: {html_path}")
