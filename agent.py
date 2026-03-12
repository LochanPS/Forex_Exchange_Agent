"""
AgentPay - Invoice Extraction Agent
Uses Google Gemini Flash 2.5 for invoice field extraction
"""
import os
import logging
import fitz  # PyMuPDF
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def extract_pdf_text(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"Failed to extract PDF text: {e}")
        raise


def extract_invoice_fields(pdf_path: str) -> dict:
    """
    Extract structured invoice fields using Gemini Flash 2.5
    Returns: {vendor, amount_usd, usdc_amount, dest_wallet, due_date, invoice_id, currency}
    """
    logger.info(f"Extracting invoice fields from {pdf_path}")
    
    # Extract text from PDF
    pdf_text = extract_pdf_text(pdf_path)
    
    if not pdf_text:
        raise ValueError("PDF contains no extractable text")
    
    # Initialize Gemini client
    client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    
    # Define the extraction prompt
    prompt = f"""Extract the following fields from this invoice:
- vendor: Company name issuing the invoice
- amount_usd: Total amount in USD (numeric only)
- usdc_amount: Same as amount_usd (for USDC payment)
- dest_wallet: Ethereum wallet address (0x...)
- due_date: Payment due date (YYYY-MM-DD format)
- invoice_id: Invoice number/ID
- currency: Currency code (e.g., USD)

Invoice text:
{pdf_text}

Return ONLY a JSON object with these exact fields. If a field is not found, use null.
"""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json"
            )
        )
        
        # Parse response
        import json
        result = json.loads(response.text)
        
        logger.info(f"Extracted fields: Vendor={result.get('vendor')}, Amount={result.get('usdc_amount')} USDC")
        return result
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        raise
