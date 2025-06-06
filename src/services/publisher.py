import pytz, asyncio
from loguru import logger
from core.config import ConfigLoader
from core.database import DataBase
from core.utils import EnvTools
from services.msg_construct import MessageConstructor
from services.telegram_bot import TelegramService




class MessagePublisher:
    def __init__(self, telegram_service: TelegramService):
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.data_base = DataBase()
        self.constructor = MessageConstructor()
        self.telegram_service = telegram_service
        self.time_zone = pytz.timezone(self.config.get("scheduler", "timezone"))

    
    def publish_for_name(self, data_name):
        self.id, self.tg_id, self.name = data_name
        posting_message = self.constructor.construct_message(self.name)

        if posting_message:
            logger.info(f"Constructed message for {self.name}: {posting_message}")
            try:
                asyncio.run_coroutine_threadsafe(
                    self.telegram_service.send_message(self.tg_id, posting_message),
                    self.telegram_service.loop
                )
            except Exception as ex:
                logger.error(f"Failed to send constructed message to chat: {ex}")
        else:
            logger.error(f"Failed to construct message for publishing")


    def publish_for_names(self, names_list):
        try:
            for data_name in names_list:
                self.publish_for_name(data_name)

        except Exception as ex:
            logger.error(f"error with publishing for every name: {ex}")


    def scheduled_publish(self):
        logger.info("Starting scheduled publish")

        match self.config.get("project", "debug_mode"):
            case True:
                self.publish_for_name((self.env_tools.load_env_var("test_id"), self.env_tools.load_env_var("test_tg_id"), self.env_tools.load_env_var("test_name")))
            case default:
                self.publish_for_names(self.data_base.get_channels())

        


