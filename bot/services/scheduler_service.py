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
        logger.debug(f"=== SCHEDULER SERVICE START ===")

        try:
            if not self.scheduler.running:
                logger.debug("Scheduler not running, initializing...")

                # Start APScheduler FIRST
                logger.debug("Starting APScheduler...")
                self.scheduler.start()

                # THEN load all configured daily summary jobs
                logger.debug("Loading daily summary jobs from database...")
                await self._load_daily_summary_jobs()

                # Add heartbeat job
                self._add_heartbeat_job()

                # Log current jobs
                jobs = self.get_scheduled_jobs()
                logger.info(f"=== SCHEDULER STARTED - {len(jobs)} JOBS LOADED ===")
                if not jobs:
                    logger.warning(
                        "Scheduler warning: No scheduled jobs found after loading."
                    )
                else:
                    for job in jobs:
                        logger.info(
                            f"-> Job Loaded: ID={job['id']}, Name='{job['name']}', Next Run (UTC): {job['next_run']}"
                        )
            else:
                logger.warning("Scheduler was already running")

        except Exception as e:
            logger.error(f"=== SCHEDULER START FAILED ===")
            logger.error(f"Error starting scheduler: {e}", exc_info=True)
            raise

    async def _load_daily_summary_jobs(self):
        """Load all daily summary jobs from database configuration"""
        logger.debug("=== LOADING DAILY SUMMARY JOBS ===")

        try:
            # Import here to avoid circular imports
            from bot.services.database_service import db_service

            # Get all chats with daily summaries enabled
            logger.debug("Querying database for daily summary configurations...")
            configs = await db_service.get_all_daily_summary_configs()

            logger.info(f"Found {len(configs)} daily summary configurations")
            jobs_created = 0

            # Create a job for each chat
            for config in configs:
                chat_id = config["chat_id"]
                hour = config["daily_summary_hour"]

                logger.debug(f"Processing config - Chat: {chat_id}, Hour: {hour}")

                if hour != "off":
                    self.add_daily_summary_job(chat_id, hour)
                    jobs_created += 1
                else:
                    logger.debug(f"Skipping chat {chat_id} - daily summary is off")

            logger.info(f"Successfully created {jobs_created} daily summary jobs")

        except Exception as e:
            logger.error(f"Failed to load daily summary jobs: {e}", exc_info=True)

    def add_daily_summary_job(self, chat_id: int, hour: str):
        """Add or update a daily summary job for a specific chat.

        Args:
            chat_id: The chat ID
            hour: The hour to send the summary ('00', '03', '08', '12', '18', '21')
        """
        logger.debug(f"=== ADDING DAILY SUMMARY JOB ===")
        logger.debug(f"Chat ID: {chat_id}, Hour: {hour}")

        try:
            # Validate hour format
            if not hour.isdigit() or not (0 <= int(hour) <= 23):
                raise ValueError(f"Invalid hour format: {hour}. Must be 00-23")

            job_id = f"daily_summary_{chat_id}"

            # Check if scheduler is running
            if not self.scheduler.running:
                logger.warning(
                    f"Scheduler not running, cannot add job for chat {chat_id}"
                )
                raise RuntimeError("Scheduler is not running")

            # Create a cron trigger for the specified hour (Madrid timezone)
            trigger = CronTrigger(
                hour=int(hour), minute=0, timezone=pytz.timezone("Europe/Madrid")
            )
            logger.debug(f"Created cron trigger for {hour}:00 Madrid time")

            # Import here to avoid circular imports
            from bot.services.daily_summary_service import send_daily_summary_for

            # Remove existing job if present
            existing_job = self.scheduler.get_job(job_id)
            if existing_job:
                logger.debug(f"Removing existing job {job_id}")
                self.scheduler.remove_job(job_id)

            # Add the job
            job = self.scheduler.add_job(
                send_daily_summary_for,
                trigger=trigger,
                id=job_id,
                name=f"Daily summary for chat {chat_id}",
                replace_existing=True,
                args=[chat_id],
            )

            logger.info(
                f"✅ Successfully added daily summary job for chat {chat_id} at {hour}:00"
            )
            logger.debug(f"Job next run time: {job.next_run_time}")

            # Verify job was added
            verify_job = self.scheduler.get_job(job_id)
            if verify_job:
                logger.debug(f"Job verification successful: {verify_job.id}")
            else:
                logger.error(
                    f"Job verification failed: job {job_id} not found after adding"
                )

        except Exception as e:
            logger.error(
                f"❌ Error adding daily summary job for chat {chat_id}: {e}",
                exc_info=True,
            )
            raise

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
            logger.error(
                f"Error removing daily summary job for chat {chat_id}: {e}",
                exc_info=True,
            )

    def update_daily_summary_job(self, chat_id: int, hour: str):
        """Update the daily summary job for a chat based on configuration.

        Args:
            chat_id: The chat ID
            hour: The new hour setting ('00', '03', '08', '12', '18', '21', 'off')
        """
        try:
            if hour == "off":
                self.remove_daily_summary_job(chat_id)
            else:
                self.add_daily_summary_job(chat_id, hour)

        except Exception as e:
            logger.error(
                f"Error updating daily summary job for chat {chat_id}: {e}",
                exc_info=True,
            )

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
                    "id": job.id,
                    "name": job.name,
                    "next_run": (
                        job.next_run_time
                        if self.scheduler.running
                        else "Not scheduled (scheduler not running)"
                    ),
                }
                jobs.append(job_info)
            return jobs
        except Exception as e:
            logger.error(f"Error getting scheduled jobs: {e}", exc_info=True)
            return []

    def _add_heartbeat_job(self):
        """Add a heartbeat job that logs every 10 minutes to verify scheduler is alive"""
        try:
            trigger = CronTrigger(
                minute="*/10",  # Every 10 minutes
                timezone=pytz.timezone("Europe/Madrid"),
            )

            self.scheduler.add_job(
                func=self._scheduler_heartbeat,
                trigger=trigger,
                id="scheduler_heartbeat",
                name="Scheduler Heartbeat",
                replace_existing=True,
            )

            logger.info("Scheduler heartbeat job added (every 10 minutes)")

        except Exception as e:
            logger.error(f"Failed to add heartbeat job: {e}", exc_info=True)

    def _scheduler_heartbeat(self):
        """Log a heartbeat message to verify scheduler is alive"""
        jobs_count = len(self.scheduler.get_jobs())
        logger.info(f"💓 Scheduler heartbeat - {jobs_count} jobs active")
        return


scheduler_service = SchedulerService()  # Single instance
