import os
from dotenv import load_dotenv
from logger import get_app_logger


class _Config:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(_Config, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def getenv_or_throw(self, key: str, redacted: bool = True) -> str:
        value: str | None = os.getenv(key)
        if not value:
            raise KeyError(f"Missing environment variable: {key}")
        if redacted:
            self.logger.debug(f"{key} = ***REDACTED***")
        else:
            self.logger.debug(f"{key} = {value}")
        return value

    def getenv_int_or_throw(self, key: str, redacted: bool = True) -> int:
        value: str = self.getenv_or_throw(key, redacted)
        try:
            value_parsed = int(value)
            return value_parsed
        except ValueError as e:
            raise ValueError(f"Environment variable {key} must be a valid integer")

    def _init(self):
        self.logger = get_app_logger()
        load_dotenv()

        # Core
        self.DEBUG = self.getenv_or_throw("DEBUG", redacted=False).lower() in (
            "true",
            "1",
        )
        self.ALLOW_ORIGINS = self.getenv_or_throw(
            "ALLOW_ORIGINS", redacted=False
        ).split(",")
        self.SECRET_KEY = self.getenv_or_throw("SECRET_KEY", redacted=True)

        # PostgreSQL
        self.PG_USER = self.getenv_or_throw("PG_USER", redacted=False)
        self.PG_PASSWORD = self.getenv_or_throw("PG_PASSWORD", redacted=True)
        self.PG_HOST = self.getenv_or_throw("PG_HOST", redacted=False)
        self.PG_PORT = self.getenv_int_or_throw("PG_PORT", redacted=False)
        self.PG_NAME = self.getenv_or_throw("PG_NAME", redacted=False)

        # Redis
        self.REDIS_HOST = self.getenv_or_throw("REDIS_HOST", redacted=False)
        self.REDIS_PORT = self.getenv_int_or_throw("REDIS_PORT", redacted=False)
        self.REDIS_DB = self.getenv_or_throw("REDIS_DB", redacted=False)
        self.REDIS_PASSWORD = self.getenv_or_throw("REDIS_PASSWORD", redacted=True)

        # SMTP
        self.EMAIL_ADDRESS = self.getenv_or_throw("EMAIL_ADDRESS", redacted=False)
        self.EMAIL_PASSWORD = self.getenv_or_throw("EMAIL_PASSWORD", redacted=True)


config = _Config()
