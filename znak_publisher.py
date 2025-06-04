from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

from collections import deque
import random, os, sys, inspect, pytz, logging, toml, telebot

from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger

# -1002392744548



# Setuping the exception handler
class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = inspect.currentframe(), 0
        while frame and depth < 10:
            if frame.f_code.co_filename == logging.__file__:
                depth += 1
            frame = frame.f_back

        logger.opt(depth=depth, exception=record.exc_info, record=True).log(
            level, record.getMessage()
        )



class ConfigLoader:
    __instance = None # char " _ " is used to indicate that this is a private variable
    __config = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._load()
        return cls.__instance

    @classmethod
    def _load(cls):
        try:
            with open("pyproject.toml", "r") as f:
                cls.__config = toml.load(f)
            os.environ["CONFIG_LOADED"] = "1"
        except Exception as error:
            logger.critical("Config load failed: {error}", error=error)
            raise
   
    @classmethod
    def get(cls, section: str, key: str = None):
        if key is None:
            return cls.__config.get(section, {})
        return cls.__config[section][key]
    
    def __getitem__(self, section: str):
        return self.get(section)



class DockerTools:
    @staticmethod
    def is_running_inside_docker():
        try:
            if os.environ['RUNNING_INSIDE_DOCKER'] == "1":
                return True
        except KeyError:
            ()
        return False



class LogSetup:
    def __init__(self):
        self.configure_loguru()

    @staticmethod
    def configure_loguru():
        logger.remove()
        logger.add(
            "debug/debug.json",
            format="{time} {level} {message}",
            serialize=True,
            rotation="04:00",
            retention="14 days",
            compression="zip",
            level="DEBUG",
            catch=True,
        )

        logger.add(
            sys.stdout,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> – {message}",
            level="DEBUG",
            catch=True,
        )







class ZnakPublisherService():
    def __init__(self):
        self.config = ConfigLoader()
        self.scheduler = BlockingScheduler(timezone=pytz.timezone(self.config.get("publisher", "timezone")))
        self.publisher = MessagePublisher()


    def __getitem__(self, item):
        return getattr(self, item)
    

    def ShowPublisherParams(self):
        if self.config.get("project", "show_publisher_params_on_run"):
            from tabulate import tabulate

            table = self.config["publisher"]

            logger.info(f"ZnakPublisherService started with parameters:")
            print(tabulate([table],
                           headers="keys",
                           tablefmt="grid"))


    @logger.catch
    def run_service(self):
        LogSetup()
        self.ShowPublisherParams()
        
        

        # 3 раза в сутки: 8:00, 14:00, 20:00 (МСК)
        # scheduler.add_job(scheduled_publish, 'cron', hour='8,14,20')

        self.scheduler.add_job(self.publisher.scheduled_publish, 'interval', seconds=5)
        self.scheduler.start()



class MessagePublisher():
        @logger.catch
        def scheduled_publish(self):
            logger.info("Scheduled publish job started")
            # publisher = MessagePublisher()
            # publisher.publish_all()





if __name__ == "__main__":
    try:
        ZnakPublisherService().run_service()
    except KeyboardInterrupt:
        logger.info("Service stopped by user")
    except Exception as error:
        logger.critical(f"Service crashed: {error}")
        sys.exit(1)