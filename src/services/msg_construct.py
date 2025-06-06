from apscheduler.schedulers.blocking import BlockingScheduler
import random
from loguru import logger
from core.config import ConfigLoader
from core.utils import JsonLoader, Filters




class MessageConstructor:
    def __init__(self):
        self.config = ConfigLoader()
        self.json_loader = JsonLoader()
        self.filters = Filters()
        self.artifact = self.config.get("msg_construct", "artifact")
        self.max_history = self.config.get("msg_construct", "max_history")
        self.data_path = self.config.get("msg_construct", "data_path")
        self.messages = self.config.get("msg_construct", "messages")
        self.message_history = self.config.get("msg_construct", "message_history")
        
        self.message_file = f"{self.data_path}/{self.messages}"
        self.message_history_file = f"{self.data_path}/{self.message_history}"

        self.history = self._load_history()


    #TODO: ALL OF THIS WILL BE WORK WITH SQL DATABASE IN FUTURE
    

    def _load_history(self):
        try:
            return self.json_loader.readJson(self.message_history_file)
        except FileNotFoundError:
            logger.info("History file not found. Starting with empty history.")
            return {}
        except Exception as e:
            logger.error(f"Error loading history from JSON: {e}. Starting with empty history.")
            return {}


    def _save_history(self):
        try:
            self.json_loader.writeJson(self.message_history_file, self.history)
        except Exception as e:
            logger.error(f"Failed to save history to '{self.message_history_file}': {e}")


    def _update_history(self, name, message):
        if name not in self.history or not isinstance(self.history.get(name), list):
            self.history[name] = []

        self.history[name].append(message)
        
        if len(self.history[name]) > self.max_history:
            self.history[name] = self.history[name][-self.max_history:]

        self._save_history()


    def is_message_exists_in_history(self, name, message):
        return name in self.history and message in self.history[name]
    

    def clear_history_for_name(self, name):
        self.history[name] = []
        self._save_history()

    
    def clear_history_for_name(self, name):
        self.history[name] = []
        self._save_history()


    def pick_random_message(self, name, type):
        messages_list = self.json_loader.readJson(self.message_file)[type]
        
        try:
            messages_history_list = self.json_loader.readJson(self.message_history_file)[name]
            available_messages = self.filters.filter_strings(messages_list, messages_history_list)
        except:
            available_messages = messages_list
        
        if len(available_messages) != 0:
            return random.choice(available_messages)
        else:
            return False
 

    def construct_message(self, name, type):
        message = None

        for _ in range(5):
            candidate = self.pick_random_message(name, type)
            if candidate:
                message = candidate
                break

        if not message:
            logger.error(f"Failed to find unique message for '{name}'")
            return None
        else:
            self._update_history(name, message)
            return self.filters.personalized_line(message, self.artifact, name)