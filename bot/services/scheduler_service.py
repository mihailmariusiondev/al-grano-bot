import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.services.daily_summary_service import send_daily_summaries
from bot.utils.logger import logger

logger = logger.get_logger(__name__)

class SchedulerService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(self):
        if not self.initialized:
            self.scheduler = AsyncIOScheduler()
            self.initialized = True

    def start(self):
        """Start the scheduler"""
        try:
            if not self.scheduler.running:
                self.scheduler.add_job(
                    send_daily_summaries,
                    CronTrigger(
                        hour=3, minute=0, timezone=pytz.timezone("Europe/Madrid")
                    ),
                    id="daily_summaries",
                    name="Generate daily chat summaries",
                    replace_existing=True,
                )
                self.scheduler.start()
                logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}", exc_info=True)
            raise

    def stop(self):
        """Stop the scheduler"""
        try:
            if self.scheduler.running:
                # MODIFICATION: Make shutdown non-blocking
                self.scheduler.shutdown(wait=False)
                logger.info("Scheduler shutdown initiated (non-blocking).")
        except Exception as e:
            # Log error but don't re-raise if the goal is quick exit.
            logger.error(f"Error initiating scheduler shutdown: {e}", exc_info=True)

scheduler_service = SchedulerService()  # Single instance