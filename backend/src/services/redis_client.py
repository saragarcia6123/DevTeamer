import redis.asyncio as redis

from logger import get_redis_logger
from config import config


class _RedisClient:

    async def test_connection(self) -> bool:
        self.logger.info("Testing connection to Redis...")
        try:
            await self.r.ping()
            self.logger.info("Redis connection successful")
            return True
        except Exception as e:
            self.logger.error(f"Redis connection failed: {e}")
            return False

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(_RedisClient, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        self.logger = get_redis_logger()
        self.logger.info("Initializing Redis...")

        self.r = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            password=config.REDIS_PASSWORD,
            decode_responses=True,
        )

redis_client = _RedisClient()
