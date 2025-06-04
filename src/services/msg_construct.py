from apscheduler.schedulers.blocking import BlockingScheduler
import pytz
from loguru import logger
from core.config import ConfigLoader




class MessageConstructor:
    def __init__(self):
        self.config = ConfigLoader()
        self.max_history = self.config.get("msg_construct", "max_history")


    def construct_message(self, data):
        ()