import redis
import logging


class RedisManager(object):
    def __init__(self):
        """Generates redis connection that is then passed around the application
        """
        # Connect to redis
        self.redis = redis.Redis(host="localhost", port=6379)


redis_manager = RedisManager()
logging.debug("✅ Redis Connection established")
