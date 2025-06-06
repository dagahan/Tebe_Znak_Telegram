import pytz
from loguru import logger
from core.config import ConfigLoader
from core.database import DataBase
from services.msg_construct import MessageConstructor
from services.telegram_bot import TelegramService




class MessagePublisher:
    def __init__(self):
        self.config = ConfigLoader()
        self.data_base = DataBase()
        self.constructor = MessageConstructor()
        self.time_zone = pytz.timezone(self.config.get("scheduler", "timezone"))
        # TODO:
        self.retry_count = self.config.get("publisher", "retry_count")
        self.retry_delay = self.config.get("publisher", "retry_delay")

    
    def publish_for_name(self, data_name):
        # logger.debug(data_name)
        self.id, self.tg_id, self.name = data_name

        posting_message = self.constructor.construct_message(self.name)

        match posting_message:
            case False:
                logger.error("Failed to construct message for publishing")
            case default:
                logger.info(f"Constructed message for {self.name}: {posting_message}")
                #TODO: self.telegram_bot.print_message(chat_id, posting_message)


    def publish_for_names(self, names_list):
        try:
            for data_name in names_list:
                # logger.debug(name)
                self.publish_for_name(data_name)

        except Exception as ex:
            logger.error(f"error with publishing for every name: {ex}")


    def scheduled_publish(self):
        logger.info("Starting scheduled publish")

        self.publish_for_names(self.data_base.get_channels())

        # self.publish_for_name((1, '-1002392744548', 'Алина'))


        


