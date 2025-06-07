import sqlite3, colorama
from loguru import logger
from core.config import ConfigLoader
from core.utils import EnvTools




class DataBase():
    def __init__(self):
        self.config = ConfigLoader()
        self.env_tools = EnvTools()
        self.db_path = self.config.get("database", "file_path")
        self.db_name = self.config.get("database", "file_name")
        

    @logger.catch
    def SQL_request(self, request, params=()):
        try:
            self.connect = sqlite3.connect(f"{self.db_path}{self.db_name}")
            self.cursor = self.connect.cursor()

            self.cursor.execute(request, params)
            self.connect.commit()
            
            result = self.cursor.fetchall()

            self.connect.close()

            if request.strip().upper().startswith("SELECT"):
                # logger.debug(f"""{colorama.Fore.BLUE}SQL: {request}
                #              Result: {result}""")
                return result 
            else:
                logger.debug(f"{colorama.Fore.GREEN}SQL executed: {request}")

        except sqlite3.Error as ex:
            logger.error(f"Database error: {ex}")
            logger.error(f"Failed query: {request}")
            raise


    def create_base_structure(self):
        self.SQL_request("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tg_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL
        )""")
    
        logger.info(f"{colorama.Fore.GREEN}Database structure created")


    @logger.catch
    def insert_channel(self, tg_id, name):
        query = """
        INSERT INTO channels (tg_id, name)
        VALUES (?, ?)
        """
        self.SQL_request(query, (tg_id, name))
        return self.cursor.lastrowid

    
    @logger.catch
    def get_channels(self):
        result = self.SQL_request("""SELECT * FROM channels""")
        return result



    def setup(self):
        if not self.env_tools.is_file_exist(self.db_path, self.db_name):
            logger.debug("creating db...")
            self.env_tools.create_file_in_directory(self.db_path, self.db_name)
            logger.debug("db has been created... Now creating base structure of it,")
            self.create_base_structure()
            logger.critical(f"{colorama.Fore.GREEN}Great! Database of channels now done, please insert your data into it and run program again!")
        
        # self.insert_channel(
        #     tg_id="-1002392744548",
        #     name="Алина"
        # )

        # self.insert_channel(
        #     tg_id="-1002454106093",
        #     name="Вика"
        # )

        # self.insert_channel(
        #     tg_id="-1002258674996",
        #     name="Настя"
        # )

        # self.insert_channel(
        #     tg_id="-1002468795584",
        #     name="Лера"
        # )

        # self.insert_channel(
        #     tg_id="-1002344839925",
        #     name="Ксюша"
        # )

        # self.insert_channel(
        #     tg_id="-1002454378134",
        #     name="Лиза"
        # )

        # self.insert_channel(
        #     tg_id="-1002470954597",
        #     name="Маша"
        # )

        # self.insert_channel(
        #     tg_id="-1002434800529",
        #     name="Полина"
        # )

        # self.insert_channel(
        #     tg_id="-1002458228603",
        #     name="Аня"
        # )

        # self.insert_channel(
        #     tg_id="-1002351719046",
        #     name="Даша"
        # )

        # self.insert_channel(
        #     tg_id="-1002418708714",
        #     name="Катя"
        # )
        
        # result = self.SQL_request("SELECT * FROM channels")
        ()

    