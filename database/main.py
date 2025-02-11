from configparser import ConfigParser
from sqlmodel import Session, create_engine

class DatabaseHandler:
    def __init__(self):
        parser = ConfigParser()
        parser.read("config.ini")

        user = parser.get("Database", "user")
        password = parser.get("Database", "password")
        host = parser.get("Database", "host")
        port = parser.getint("Database", "port")
        database = parser.get("Database", "database")

        self.engine = create_engine(f"mariadb+mariadbconnector://{user}:{password}@{host}:{port}/{database}")
        self.connection = self.engine.connect()
        self.session = Session(self.engine)