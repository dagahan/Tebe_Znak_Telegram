from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
from loguru import logger
from core.config import ConfigLoader
from services.publisher import MessagePublisher




class SchedulerService:
    def __init__(self):
        self.config = ConfigLoader()
        self.service_name = self.config.get("project", "name")
        self.publisher = MessagePublisher()
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(self.config.get("publisher", "timezone")))
        self.hours = self.config.get("publisher", "post_hours")
        self.minutes = self.config.get("publisher", "post_minutes")


    def service_start_message(self):
        match self.config.get("project", "show_publisher_params_on_run"):
            case True:
                from tabulate import tabulate
                table = self.config["publisher"]
            
                logger.info(f"""{self.service_name} started with parameters:\n
                {tabulate([table], headers="keys", tablefmt="grid")}""")

            case default:
                logger.info(f"{self.service_name} started successfully!")


    def setup_jobs(self):
        match self.config.get("project", "debug_mode"):
            case True:
                self.scheduler.add_job(self.publisher.scheduled_publish,'interval',seconds=30)
                logger.warning("Running in DEBUG mode")

            case default:
                self.scheduler.add_job(
                        self.publisher.scheduled_publish,
                        'cron',
                        hour=self.hours,
                        minute=self.minutes,
                    )
                logger.info(f"Job scheduled: {self.hours}:{self.minutes}")
                    

    def run_service(self):
        self.setup_jobs()
        self.service_start_message()
        self.scheduler.start()