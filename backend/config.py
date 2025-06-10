import os
from dotenv import load_dotenv

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        load_dotenv()
        
        debug_value = os.getenv("DEBUG", "false").lower()
        self.DEBUG = debug_value in ("true", "1", "yes")
        self.SECRET_KEY = os.getenv("SECRET_KEY")

        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")
        self.DB_HOST = os.getenv("DB_HOST") or 'localhost'
        self.DB_PORT = os.getenv("DB_PORT") or '5432'
        self.DB_NAME = os.getenv("DB_NAME")

        self.REDIS_HOST = os.getenv("REDIS_HOST") or 'localhost'
        self.REDIS_PORT = os.getenv("REDIS_PORT") or '6379'
        self.REDIS_DB = os.getenv("REDIS_DB") or '0'

        self.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
