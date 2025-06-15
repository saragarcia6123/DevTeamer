import logging


def get_app_logger():
    return logging.getLogger("app")


def get_api_logger():
    return logging.getLogger("app.api")


def get_postgres_logger():
    return logging.getLogger("app.postgres")


def get_redis_logger():
    return logging.getLogger("app.redis")
