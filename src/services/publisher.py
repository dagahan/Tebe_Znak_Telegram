import random, pytz
from datetime import datetime
from loguru import logger
from core.config import ConfigLoader




class MessagePublisher:
    def __init__(self):
        self.config = ConfigLoader()
        self.telegram = TelegramService()
        self.time_zone = pytz.timezone(self.config.get("publisher", "timezone"))
        self.max_history = self.config.get("publisher", "max_history")
        # TODO:
        self.retry_count = self.config.get("publisher", "retry_count")
        self.retry_delay = self.config.get("publisher", "retry_delay")


    def scheduled_publish(self):
        logger.info("Starting scheduled publish")
        # now = datetime.now(self.time_zone)
        # is_morning = now.hour == 8
        
        # for channel_id in self.telegram.chat_ids:
        #     self.publish_to_channel(channel_id, is_morning)



class TelegramService(MessagePublisher):
    def __init__(self):
        self.config = ConfigLoader()
        # self.bot = telebot.TeleBot(self.config.get("publisher", "bot_token"))
        self.chat_ids = self.config.get("publisher", "channels_ids")

    def send_message(self, chat_id, text):
        try:
            # self.bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            if "429" in str(e):
                return self.retry_delay
            return False