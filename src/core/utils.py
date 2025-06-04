import os, json
from loguru import logger




class DockerTools:
    @staticmethod
    def is_running_inside_docker():
        try:
            if os.environ['RUNNING_INSIDE_DOCKER'] == "1":
                return True
        except KeyError:
            ()
        return False


class JsonLoader:
    @staticmethod
    def readJson(path):
        try:
            with open(os.path.abspath(path), 'rb') as file:
                raw_data = file.read()
                detected_encoding = chardet.detect(raw_data)['encoding']

            with open(os.path.abspath(path), encoding=detected_encoding) as file:
                info = json.load(file)
        except FileNotFoundError:
            info = {}
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.error(f"Error during reading JSON file {path}: {e}")
            info = {}
        return info
    

    @staticmethod
    def writeJson(path, data):
        try:
            with open(os.path.abspath(path), 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error writing JSON file {path}: {e}")