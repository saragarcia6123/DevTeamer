import redis.asyncio as redis

from config import _Config


class _RedisClient:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(_RedisClient, cls).__new__(cls)
            cls.instance._init()
        return cls.instance

    def _init(self):
        config = _Config()

        self.r = redis.Redis(
            host=config.REDIS_HOST,
            port=config.REDIS_PORT,
            db=config.REDIS_DB,
            decode_responses=True,
        )


redis_client = _RedisClient()
