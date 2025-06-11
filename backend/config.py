import os
from dotenv import load_dotenv

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._init()
        return cls._instance
    
    def getenv_or_throw(self, key: str) -> str:
        value: str | None = os.getenv(key)
        if not value:
            raise KeyError(f"Missing environment variable: {key}")
        return value
    
    def getenv_int_or_throw(self, key: str) -> int:
        value: str = self.getenv_or_throw(key)
        try:
            value_parsed = int(value)
            return value_parsed
        except ValueError as e:
            raise ValueError(f"Environment variable {key} must be a valid integer")

    def _init(self):
        load_dotenv()
        
        # Core
        self.DEBUG = self.getenv_or_throw("DEBUG").lower() in ("true", "1")
        self.ALLOW_ORIGINS = self.getenv_or_throw("ALLOW_ORIGINS").split(',')
        self.SECRET_KEY = self.getenv_or_throw("SECRET_KEY")

        # PostgreSQL
        self.DB_USER = self.getenv_or_throw("DB_USER")
        self.DB_PASSWORD = self.getenv_or_throw("DB_PASSWORD")
        self.DB_HOST = self.getenv_or_throw("DB_HOST")
        self.DB_PORT = self.getenv_int_or_throw("DB_PORT")
        self.DB_NAME = self.getenv_or_throw("DB_NAME")

        # Redis
        self.REDIS_HOST = self.getenv_or_throw("REDIS_HOST")
        self.REDIS_PORT = self.getenv_int_or_throw("REDIS_PORT")
        self.REDIS_DB = self.getenv_or_throw("REDIS_DB")

        # SMTP
        self.EMAIL_ADDRESS = self.getenv_or_throw("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD = self.getenv_or_throw("EMAIL_PASSWORD")