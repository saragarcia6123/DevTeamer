import os
from dotenv import load_dotenv


class _Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(_Config, cls).__new__(cls)
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
            raise ValueError(
                f"Environment variable {key} must be a valid integer"
            )

    def init(self):
        load_dotenv()

        # Core
        self.DEBUG = self.getenv_or_throw("DEBUG").lower() in ("true", "1")
        self.ALLOW_ORIGINS = self.getenv_or_throw("ALLOW_ORIGINS").split(',')
        self.SECRET_KEY = self.getenv_or_throw("SECRET_KEY")

        # PostgreSQL
        self.PG_USER = self.getenv_or_throw("PG_USER")
        self.PG_PASSWORD = self.getenv_or_throw("PG_PASSWORD")
        self.PG_HOST = self.getenv_or_throw("PG_HOST")
        self.PG_PORT = self.getenv_int_or_throw("PG_PORT")
        self.PG_NAME = self.getenv_or_throw("PG_NAME")

        # Redis
        self.REDIS_HOST = self.getenv_or_throw("REDIS_HOST")
        self.REDIS_PORT = self.getenv_int_or_throw("REDIS_PORT")
        self.REDIS_DB = self.getenv_or_throw("REDIS_DB")

        # SMTP
        self.EMAIL_ADDRESS = self.getenv_or_throw("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD = self.getenv_or_throw("EMAIL_PASSWORD")


config = _Config()
