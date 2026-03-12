"""
AgentPay - Test Invoice Generator
Creates sample PDF invoices for testing
"""
from fpdf import FPDF
from datetime import datetime, timedelta


def generate_sample_invoice(
    filename="inbox/sample_invoice.pdf",
    vendor="Acme Supplies Ltd",
    amount=1200.00,
    wallet="0xAbC1234567890123456789012345678901234123",
    invoice_id="INV-2026-001"
):
    """Generate a test invoice PDF"""
    
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 10, "INVOICE", ln=True, align="C")
    pdf.ln(10)
    
    # Vendor info
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 8, vendor, ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, "123 Business Street", ln=True)
    pdf.cell(0, 6, "San Francisco, CA 94102", ln=True)
    pdf.ln(10)
    
    # Invoice details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 8, "Invoice Number:", border=0)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, invoice_id, ln=True)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 8, "Date:", border=0)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, datetime.now().strftime("%Y-%m-%d"), ln=True)
    
    pdf.set_font("Arial", "B", 12)
    pdf.cell(60, 8, "Due Date:", border=0)
    pdf.set_font("Arial", "", 12)
    due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    pdf.cell(0, 8, due_date, ln=True)
    
    pdf.ln(10)
    
    # Payment details
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Payment Details", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 6, f"Wallet Address: {wallet}", ln=True)
    pdf.cell(0, 6, "Currency: USD", ln=True)
    pdf.ln(10)
    
    # Line items
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, "Description", border=1)
    pdf.cell(40, 8, "Quantity", border=1, align="C")
    pdf.cell(50, 8, "Amount", border=1, align="R", ln=True)
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(100, 8, "Professional Services", border=1)
    pdf.cell(40, 8, "1", border=1, align="C")
    pdf.cell(50, 8, f"${amount:.2f}", border=1, align="R", ln=True)
    
    pdf.ln(5)
    
    # Total
    pdf.set_font("Arial", "B", 14)
    pdf.cell(140, 10, "TOTAL DUE:", align="R")
    pdf.cell(50, 10, f"${amount:.2f} USD", align="R", ln=True)
    
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", "I", 9)
    pdf.cell(0, 6, "Please remit payment to the wallet address above.", ln=True, align="C")
    pdf.cell(0, 6, "Payment accepted in USDC on Base network.", ln=True, align="C")
    
    # Save PDF
    pdf.output(filename)
    print(f"✓ Generated: {filename}")
    print(f"  Vendor: {vendor}")
    print(f"  Amount: ${amount:.2f} USD")
    print(f"  Wallet: {wallet}")


if __name__ == "__main__":
    # Generate default sample invoice
    generate_sample_invoice()
    
    # Generate an over-limit invoice for testing
    generate_sample_invoice(
        filename="tests/fixtures/over_limit_invoice.pdf",
        vendor="Expensive Vendor Inc",
        amount=8500.00,
        wallet="0xDef9876543210987654321098765432109876543",
        invoice_id="INV-2026-999"
    )
    
    print("\n✓ Test invoices generated successfully!")
