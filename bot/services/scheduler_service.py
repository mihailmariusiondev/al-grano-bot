import pytz
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
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

    async def start(self):
        """Start the scheduler and load all configured daily summary jobs"""
        try:
            if not self.scheduler.running:
                # Load all configured daily summary jobs
                await self._load_daily_summary_jobs()

                self.scheduler.start()
                logger.info("Scheduler started successfully with dynamic jobs")
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}", exc_info=True)
            raise

    async def _load_daily_summary_jobs(self):
        """Load all daily summary jobs from database configuration"""
        try:
            # Import here to avoid circular imports
            from bot.services.database_service import db_service

            # Get all chats with daily summaries enabled
            configs = await db_service.get_all_daily_summary_configs()

            logger.info(f"Loading {len(configs)} daily summary jobs")

            # Create a job for each chat
            for config in configs:
                chat_id = config['chat_id']
                hour = config['daily_summary_hour']

                if hour != 'off':
                    self.add_daily_summary_job(chat_id, hour)

        except Exception as e:
            logger.error(f"Error loading daily summary jobs: {e}", exc_info=True)

    def add_daily_summary_job(self, chat_id: int, hour: str):
        """Add or update a daily summary job for a specific chat.

        Args:
            chat_id: The chat ID
            hour: The hour to send the summary ('00', '03', '08', '12', '18', '21')
        """
        try:
            job_id = f"daily_summary_{chat_id}"

            # Create a cron trigger for the specified hour (Madrid timezone)
            trigger = CronTrigger(
                hour=int(hour),
                minute=0,
                timezone=pytz.timezone("Europe/Madrid")
            )

            # Import here to avoid circular imports
            from bot.services.daily_summary_service import send_daily_summary_for

            # Add the job (replace if already exists)
            self.scheduler.add_job(
                send_daily_summary_for,
                trigger=trigger,
                id=job_id,
                name=f"Daily summary for chat {chat_id}",
                replace_existing=True,
                args=[chat_id]
            )

            logger.info(f"Added daily summary job for chat {chat_id} at {hour}:00")

        except Exception as e:
            logger.error(f"Error adding daily summary job for chat {chat_id}: {e}", exc_info=True)

    def remove_daily_summary_job(self, chat_id: int):
        """Remove the daily summary job for a specific chat.

        Args:
            chat_id: The chat ID
        """
        try:
            job_id = f"daily_summary_{chat_id}"

            # Remove the job if it exists
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed daily summary job for chat {chat_id}")
            else:
                logger.debug(f"No daily summary job found for chat {chat_id}")

        except Exception as e:
            logger.error(f"Error removing daily summary job for chat {chat_id}: {e}", exc_info=True)

    def update_daily_summary_job(self, chat_id: int, hour: str):
        """Update the daily summary job for a chat based on configuration.

        Args:
            chat_id: The chat ID
            hour: The new hour setting ('00', '03', '08', '12', '18', '21', 'off')
        """
        try:
            if hour == 'off':
                self.remove_daily_summary_job(chat_id)
            else:
                self.add_daily_summary_job(chat_id, hour)

        except Exception as e:
            logger.error(f"Error updating daily summary job for chat {chat_id}: {e}", exc_info=True)

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

    def get_scheduled_jobs(self):
        """Get list of currently scheduled jobs for debugging"""
        try:
            jobs = []
            for job in self.scheduler.get_jobs():
                job_info = {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time if self.scheduler.running else 'Not scheduled (scheduler not running)'
                }
                jobs.append(job_info)
            return jobs
        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {e}", exc_info=True)
            return []

scheduler_service = SchedulerService()  # Single instance