import pytz, asyncio, threading, signal, colorama
from loguru import logger
from apscheduler.schedulers.blocking import BlockingScheduler
from core.config import ConfigLoader
from services.publisher import MessagePublisher
from services.telegram_bot import TelegramService
from core.database import DataBase




class SchedulerService:
    def __init__(self):
        self.config = ConfigLoader()
        self.service_name = self.config.get("project", "name")
        self.data_base = DataBase()
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(self.config.get("scheduler", "timezone")))
        self.stop_event = threading.Event()
        self.hours = self.config.get("scheduler", "post_hours")
        
        self.bot_loop = asyncio.new_event_loop()
        self.telegram_service = TelegramService(loop=self.bot_loop)
        self.publisher = MessagePublisher(self.telegram_service)
        
        self.bot_thread = None


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


    def get_period_of_day(self, hour):
        try:
            if 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 18:
                return 'day'
            else:
                return 'evening'   
                    
        except Exception as ex:
            logger.critical(f"{colorama.Fore.RED}There is an error with checking type of posting message: {ex}") 


    def setup_jobs(self):
        match self.config.get("project", "debug_mode"):
            case True:
                period_type = self.get_period_of_day(14)
                self.scheduler.add_job(
                    lambda: self.publisher.scheduled_publish(period_type),
                    'interval',
                    seconds=5
                )
                logger.warning("Running in DEBUG mode")

            case default:
                for picked_hour in self.hours:
                    pub_time = str(picked_hour).split(":")
                    type = self.get_period_of_day(int(pub_time[0]))
                    self.scheduler.add_job(
                            lambda pt=type: self.publisher.scheduled_publish(pt),
                            'cron',
                            hour=pub_time[0],
                            minute=pub_time[1],
                            )
                    logger.info(f"Job scheduled: {picked_hour}")


    def handle_sigint(self, signum, frame):
        try:
            logger.info(f"{colorama.Fore.CYAN}{self.service_name} shutdown initiated.")
            self.scheduler.shutdown(wait=False)

        except Exception as e:
            logger.error(f"{colorama.Fore.RED}Error during {self.service_name} shutdown: {e}.")

        self.stop_event.set() # here we set the stop event to signal the bot thread to stop


    def _run_telegram_bot_loop(self):
        try:
            asyncio.set_event_loop(self.bot_loop)
            self.bot_loop.run_until_complete(self.telegram_service.start_bot())
        except Exception as e:
            logger.error(f"{colorama.Fore.RED}Telegram bot crashed: {e}")
    


    def run_service(self):
        self.data_base.setup()
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
                logger.info(f"{colorama.Fore.CYAN}Waiting for Telegram bot to shutdown...")
                self.bot_thread.join(timeout=3)
            logger.info(f"{colorama.Fore.CYAN}Service '{self.service_name}' gracefully stopped")