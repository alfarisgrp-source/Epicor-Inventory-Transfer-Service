from factory import ServiceFactory
import yaml
import logging
import os
from scheduler import start_scheduler
from config import load_config

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
    cfg = load_config()

    # Setup logging
    setup_logging(cfg)

    logging.info("=== Inventory Transfer Scheduler Starting ===")

    # Start APScheduler (runs forever)
    start_scheduler()

if __name__ == "__main__":
    main()
