from znak_publisher import *





class TelegramBot():
    def __init__(self):
        self.config = ConfigLoader()
        self.bot = aiogram.Bot(token=self.config.get("publisher", "bot_token"))
        self.dp = aiogram.Dispatcher()

    def __getitem__(self, item):
        return getattr(self, item)