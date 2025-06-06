import asyncio

from loguru import logger
from core.config import ConfigLoader
from core.utils import EnvTools, MethodTools

from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message



class TelegramService():
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.method_tools = MethodTools()
        self.bot_token = self.env_tools.load_env_var("bot_token")
        self.admin_id = self.env_tools.load_env_var("admin_id")
        self.telegram_bot = Bot(token=self.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.loop = loop or asyncio.get_event_loop()
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
        

    

    @logger.catch
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


    async def send_message(self, tg_id, message):
        try:
            await self.bot.send_message(tg_id, message)
        except Exception as ex:
            logger.error(f"There is an error with {self.method_tools.name_of_method()}")