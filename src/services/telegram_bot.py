import asyncio
from loguru import logger
from core.config import ConfigLoader

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message



class TelegramService():
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.config = ConfigLoader()
        self.bot_token = self.config.get("telegram_bot", "bot_token")
        self.chat_ids = self.config.get("telegram_bot", "channels_ids")
        self.telegram_bot = Bot(token=self.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

        self.loop = loop
        self.bot = Bot(
            token=self.bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML),
            loop=self.loop
        )
        self.dp = Dispatcher()

        @self.dp.message(CommandStart())
        async def cmd_start_handler(message: Message):
            await message.answer("Привет! Бот запущен и готов к работе.")

        self._stop_event = asyncio.Event()
    

    async def start_bot(self):
        logger.info("Starting Telegram bot polling")
        polling_task = asyncio.create_task(self.dp.start_polling(self.bot))
        await self._stop_event.wait() # await until stop event is set from scheduler

        polling_task.cancel()
        try:
            await polling_task
        except Exception as e:
            logger.error(f"Error while stopping polling: {e}")

        await self.bot.session.close()
        logger.info("Telegram bot stopped gracefully")