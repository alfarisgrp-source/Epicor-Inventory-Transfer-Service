from factory import ServiceFactory
import yaml
import logging
import os


def setup_logging(cfg):
    log_file = cfg["logging"]["file"]
    log_level = getattr(logging, cfg["logging"]["level"].upper(), logging.INFO)
    encoding = cfg["logging"].get("encoding", "utf-8")  # Get encoding from config

    # Ensure the log directory exists
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create handlers with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding=encoding)
    
    # For console handler, we need to handle it differently on Windows
    import sys
    if sys.platform == 'win32':
        # Windows console might need special handling
        console_handler = logging.StreamHandler(sys.stdout)
        if hasattr(console_handler.stream, 'reconfigure'):
            console_handler.stream.reconfigure(encoding=encoding)
    else:
        console_handler = logging.StreamHandler()
    
    # Configure logging with both handlers
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            file_handler,
            console_handler
        ]
    )

def main():
    # Load config
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    # Setup logging before anything else
    setup_logging(cfg)

    logging.info("Starting inventory transfer process...")

    factory = ServiceFactory()
    inv_transfer = factory.inventory_transfer()

    # Run the entire transfer flow (token creation handled internally)
    inv_transfer.start_transfer_flow(cfg["epicor"]["default_password"])

    logging.info("[OK] All transfers processed successfully. Check logs/transfer.log for details.")

if __name__ == "__main__":
    main()
