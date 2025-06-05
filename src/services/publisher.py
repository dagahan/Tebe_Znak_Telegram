import pytz
from loguru import logger
from core.config import ConfigLoader
from services.msg_construct import MessageConstructor
from services.telegram_bot import TelegramService




class MessagePublisher:
    def __init__(self):
        self.config = ConfigLoader()
        self.constructor = MessageConstructor()
        self.time_zone = pytz.timezone(self.config.get("scheduler", "timezone"))
        # TODO:
        self.retry_count = self.config.get("publisher", "retry_count")
        self.retry_delay = self.config.get("publisher", "retry_delay")

    
    def publish_for_name(self, name):
        posting_message = self.constructor.construct_message(name)

        match posting_message:
            case False:
                logger.error("Failed to construct message for publishing")
            case default:
                logger.info(f"Constructed message for {name}: {posting_message}")
                #TODO: self.telegram_bot.print_message(chat_id, posting_message)


    def scheduled_publish(self):
        logger.info("Starting scheduled publish")

        # load all list of names and do method for every active name
        self.publish_for_name("Жопка")


        


