# scheduler.py

import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
from zoneinfo import ZoneInfo

from factory import ServiceFactory


logger = logging.getLogger("Scheduler")


def run_inventory_transfer():
    """
    This function runs your existing inventory transfer flow.
    It is triggered by APScheduler every 30 minutes.
    """
    saudi_time = datetime.now(ZoneInfo("Asia/Riyadh"))
    logger.info(f"Running scheduled job at Saudi time: {saudi_time}")

    try:
        factory = ServiceFactory()
        inv_transfer = factory.inventory_transfer()

        # Same as your main.py flow
        from config import load_config
        cfg = load_config()

        inv_transfer.start_transfer_flow(cfg["epicor"]["default_password"])

        logger.info("✓ Scheduled inventory transfer completed successfully.")

    except Exception as e:
        logger.exception(f"❌ Scheduled inventory transfer failed: {str(e)}")


def start_scheduler():
    """
    Creates a scheduler that runs every 30 minutes using Saudi timezone.
    """
    logger.info("Starting APScheduler...")

    scheduler = BlockingScheduler(timezone="Asia/Riyadh")

    # Add Job
    scheduler.add_job(
        run_inventory_transfer,
        trigger=IntervalTrigger(minutes=30),
        id="inventory_transfer_job",
        replace_existing=True  # Avoids duplicate jobs on restart
    )

    logger.info("Scheduler started. Job will run every 30 minutes (Saudi time).")

    # Start scheduler
    scheduler.start()
