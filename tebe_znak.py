import os
import sys
import telebot
import random
import time
import json
from datetime import datetime

# Установка зависимостей
os.system("pip install -r requirements.txt")

# Токен бота и массив каналов
TOKEN = "7064737344:AAFk4zcdHiEcipfWNCXNWabf70lFJch9LAQ"
CHAT_IDS = ["-1002290461483", "-1002258674996", "-1002454106093"]

bot = telebot.TeleBot(TOKEN)

# Функция для загрузки сообщений из JSON
def load_messages(channel_index):
    file_path = f"data/{channel_index}/messages.json"
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return data["messages"]

# Функция для загрузки истории сообщений
def load_message_history(channel_index):
    history_file = f"data/{channel_index}/message_history.json"
    try:
        with open(history_file, "r", encoding="utf-8") as file:
            return json.load(file).get("last_messages", [])
    except FileNotFoundError:
        return []

# Функция для сохранения истории сообщений
def save_message_history(channel_index, history):
    history_file = f"data/{channel_index}/message_history.json"
    os.makedirs(f"data/{channel_index}", exist_ok=True)
    with open(history_file, "w", encoding="utf-8") as file:
        json.dump({"last_messages": history}, file, ensure_ascii=False, indent=4)

# Функция для выбора уникального сообщения
def get_unique_message(messages, message_history):
    while True:
        message = random.choice(messages)
        if message not in message_history:
            return message

# Функция отправки сообщения в канал
def send_message(channel_index, chat_id):
    messages = load_messages(channel_index)
    message_history = load_message_history(channel_index)

    # Получение уникального сообщения
    message = get_unique_message(messages, message_history)
    formatted_message = f"{message}"

    try:
        bot.send_message(chat_id=chat_id, text=formatted_message)
        print(f"Отправлено сообщение в канал {chat_id}:\n{formatted_message}\n")

        # Обновление истории сообщений
        message_history.append(message)
        if len(message_history) > 200:
            message_history.pop(0)
        save_message_history(channel_index, message_history)
    except telebot.apihelper.ApiTelegramException as e:
        if "429" in str(e):
            retry_after = int(e.result_json.get("parameters", {}).get("retry_after", 60))
            print(f"Слишком много запросов для канала {chat_id}. Ожидание {retry_after} секунд...")
            time.sleep(retry_after)
        else:
            print(f"Ошибка отправки сообщения в канал {chat_id}: {e}")

# Основной цикл
if __name__ == "__main__":
    while True:
        for index, chat_id in enumerate(CHAT_IDS):
            send_message(index, chat_id)
        print("Задержка перед следующей отправкой: 4 часа.")
        time.sleep(14400)  # 4 часа в секундах