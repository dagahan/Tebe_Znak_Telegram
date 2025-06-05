import os, sqlite3
from loguru import logger



class DataBase():
    def __init__(self):
        pass


    def create_base_structure(self):
        try:
            conn = sqlite3.connect("/home/usov/myprojects/Tebe_Znak_Telegram/database/database.db")


            c = conn.cursor()


            c.execute("""CREATE TABLE channels (
                    id integer,
                    ig_id text,
                    name text
                    )""")


            conn.commit()
            conn.close()
        except Exception as ex:
            logger.error(f"There is an error with database: {ex}")