from configparser import ConfigParser
from sqlalchemy import NullPool
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

        self.engine = create_engine(
            f"mariadb+mariadbconnector://{user}:{password}@{host}:{port}/{database}", 
            pool_size=20, 
            pool_pre_ping=True, 
            max_overflow=5
        )

    def get_session(self):
        with Session(self.engine) as session:
            yield session