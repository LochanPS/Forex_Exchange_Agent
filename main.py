"""
AgentPay - Main Entry Point
Folder watcher that orchestrates the invoice payment pipeline
"""
import os
import sys
import time
import json
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
import agent
import compliance
import payment
import receipt

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
log_file = os.getenv("LOG_FILE", "logs/agentpay.log")

# Ensure logs directory exists
Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s %(levelname)-8s [%(name)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("AgentPay")


class InvoiceHandler(FileSystemEventHandler):
    """Handles new PDF files dropped into inbox/"""
    
    def on_created(self, event):
        if event.is_directory:
            return
        
        if not event.src_path.endswith('.pdf'):
            return
        
        # Wait a moment for file to be fully written
        time.sleep(1)
        
        self.process_invoice(event.src_path)
    
    def process_invoice(self, pdf_path: str):
        """Main pipeline: extract → validate → pay → receipt"""
        filename = Path(pdf_path).stem
        
        try:
            logger.info(f"New invoice detected: {Path(pdf_path).name}")
            
            # Step 1: Extract invoice fields using Gemini
            invoice_data = agent.extract_invoice_fields(pdf_path)
            
            # Step 2: Validate compliance
            compliance_result = compliance.validate_invoice(invoice_data)
            
            if compliance_result["status"] == "HOLD":
                # Save to exceptions folder
                exception_path = f"exceptions/hold_{filename}.json"
                with open(exception_path, "w") as f:
                    json.dump({
                        "invoice": invoice_data,
                        "compliance": compliance_result,
                        "status": "HOLD"
                    }, f, indent=2)
                
                logger.warning(f"Exception saved: {exception_path}")
                return
            
            # Step 3: Execute payment
            payment_result = payment.execute_payment(invoice_data)
            
            # Step 4: Generate receipt
            receipt.generate_receipt(invoice_data, payment_result, filename)
            
            logger.info(f"✓ Payment completed: {payment_result['tx_hash']}")
            
        except Exception as e:
            logger.error(f"Pipeline failed for {filename}: {e}", exc_info=True)
            
            # Save error to exceptions
            error_path = f"exceptions/error_{filename}.json"
            with open(error_path, "w") as f:
                json.dump({
                    "filename": filename,
                    "error": str(e),
                    "status": "ERROR"
                }, f, indent=2)


def main():
    """Start the folder watcher"""
    logger.info("=" * 60)
    logger.info("AgentPay - Autonomous Invoice Settlement Agent")
    logger.info("=" * 60)
    
    # Verify environment
    required_vars = [
        "GOOGLE_API_KEY",
        "PRIVATE_KEY",
        "WALLET_ADDRESS",
        "BASE_TESTNET_RPC_URL",
        "USDC_TESTNET_ADDRESS"
    ]
    
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Copy .env.example to .env and fill in all values")
        sys.exit(1)
    
    # Ensure directories exist
    Path("inbox").mkdir(exist_ok=True)
    Path("settled").mkdir(exist_ok=True)
    Path("exceptions").mkdir(exist_ok=True)
    
    # Start watcher
    event_handler = InvoiceHandler()
    observer = Observer()
    observer.schedule(event_handler, "inbox", recursive=False)
    observer.start()
    
    logger.info("Watcher started. Monitoring inbox/ for new invoices...")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping watcher...")
        observer.stop()
    
    observer.join()
    logger.info("AgentPay stopped")


if __name__ == "__main__":
    main()
