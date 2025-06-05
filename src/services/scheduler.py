import pytz, asyncio, threading, signal
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from core.config import ConfigLoader
from services.publisher import MessagePublisher
from services.telegram_bot import TelegramService




class SchedulerService:
    def __init__(self):
        self.config = ConfigLoader()
        self.service_name = self.config.get("project", "name")
        self.publisher = MessagePublisher()
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(self.config.get("scheduler", "timezone")))
        self.stop_event = threading.Event()
        self.hours = self.config.get("scheduler", "post_hours")
        self.minutes = self.config.get("scheduler", "post_minutes")
        

        self.bot_thread = None
        self.telegram_service = None


    def service_start_message(self):
        match self.config.get("project", "show_publisher_params_on_run"):
            case True:
                from tabulate import tabulate
                table = self.config["publisher"]
                table.update(self.config["scheduler"])
                table.update(self.config["msg_construct"])
                table.update(self.config["telegram_bot"])
            
                logger.info(f"""{self.service_name} started with parameters:\n
                {tabulate([table], headers="keys", tablefmt="grid")}""")

            case default:
                logger.info(f"{self.service_name} started successfully!")


    def setup_jobs(self):
        match self.config.get("project", "debug_mode"):
            case True:
                self.scheduler.add_job(self.publisher.scheduled_publish,'interval',seconds=5)
                logger.warning("Running in DEBUG mode")

            case default:
                self.scheduler.add_job(
                        self.publisher.scheduled_publish,
                        'cron',
                        hour=self.hours,
                        minute=self.minutes,)
                logger.info(f"Job scheduled: {self.hours}:{self.minutes}")
                    


    def handle_sigint(self, signum, frame):
        try:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler shutdown initiated")
        except Exception as e:
            logger.error(f"Error during scheduler shutdown: {e}")
        self.stop_event.set() # here we set the stop event to signal the bot thread to stop


    def _run_telegram_bot_loop(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        self.telegram_service = TelegramService(loop=loop)
        task = loop.create_task(self.telegram_service.start_bot())

        try:
            loop.run_until_complete(task)
        except Exception as e:
            logger.error(f"Telegram bot crashed: {e}")
    


    def run_service(self):
        self.setup_jobs()
        self.service_start_message()
   
        self.bot_thread = threading.Thread(
            target=self._run_telegram_bot_loop,
            daemon=True
        )
        self.bot_thread.start()

        signal.signal(signal.SIGINT, self.handle_sigint)

        try:
            logger.info("Scheduler is starting...")
            self.scheduler.start()
        finally:
            if self.bot_thread.is_alive():
                logger.info("Waiting for Telegram bot to shutdown...")
                self.bot_thread.join(timeout=3)
            logger.info(f"Service '{self.service_name}' gracefully stopped")