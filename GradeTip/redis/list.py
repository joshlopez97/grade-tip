import traceback

from GradeTip.models import redis_server
from flask import current_app as app


class RedisList:
    def __init__(self, list_name):
        self.redis = redis_server
        self.list_name = list_name

    def push(self, value):
        try:
            return self.redis.lpush(self.list_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return 0

    def trim(self, start, end):
        try:
            return self.redis.ltrim(self.list_name, start, end)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def slice(self, start, end):
        try:
            return self.redis.lrange(self.list_name, start, end)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return []

    def length(self):
        try:
            return self.redis.llen(self.list_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None
