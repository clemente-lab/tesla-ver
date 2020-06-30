import redis


class RedisManager(object):
    def __init__(self):
        # Connect to redis
        self.redis = redis.Redis(host="data-cache", port=6379)


redis_manager = RedisManager()
