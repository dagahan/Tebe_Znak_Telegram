from telegram_bot import TelegramBot




class MessagePublisher(TelegramBot):
    @logger.catch
    def send_message(self, chat_id, message):
        logger.info(f"Sending message to {chat_id}: {message}")


    @logger.catch
    def scheduled_publish(self):
        logger.info("Scheduled publish job started")
        # publisher = MessagePublisher()
        # publisher.publish_all()