import random, pytz, threading, asyncio
from datetime import datetime
from loguru import logger
from core.config import ConfigLoader
from services.msg_construct import MessageConstructor


from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message


class MessagePublisher:
    def __init__(self):
        self.config = ConfigLoader()
        self.telegram = TelegramService()
        self.time_zone = pytz.timezone(self.config.get("scheduler", "timezone"))
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
        self.bot_token = self.config.get("telegram_bot", "bot_token")
        self.chat_ids = self.config.get("telegram_bot", "channels_ids")
        self.dispatcher = Dispatcher()
        # Initialize Bot instance with default bot properties which will be passed to all API calls
        self.telegram_bot = Bot(token=self.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        self.dispatcher.message()(self.echo_handler)

    def start_bot(self):
        def start_polling():
            # Создаем новый цикл событий для потока
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                loop.run_until_complete(
                    self.dispatcher.start_polling(
                        self.telegram_bot, 
                        handle_signals=False  # Ключевое исправление
                    )
                )
            finally:
                loop.close()

        # Создаем и запускаем поток
        bot_thread = threading.Thread(target=start_polling, daemon=True)
        bot_thread.start()
        logger.info("Telegram bot started in background thread")


    async def send_message(self, chat_id, text):
        try:
            await self.telegram_bot.send_message(chat_id=chat_id, text=text)
            return True
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            if "429" in str(e):  # Too Many Requests
                return self.config.get("publisher", "retry_delay", 5)
            return False


    async def echo_handler(self, message: Message) -> None:
        try:
            await message.send_copy(chat_id=message.chat.id)
        except TypeError:
            await message.answer("Nice try!")
        


    def echo_handler(self, message: Message) -> None:
        try:
            message.send_copy(chat_id=message.chat.id)
        except TypeError:
            message.answer("Nice try!")
            