import traceback

from GradeTip.redis import redis_server
from flask import current_app as app


class RedisList:
    """ Wrapper class for interacting with Redis lists. """
    def __init__(self, list_name):
        self.redis = redis_server
        self.list_name = list_name

    def push(self, value):
        """
        Pushes value to front of list
        :param value: value to push
        :return: number of items pushed to list
        """
        try:
            app.logger.debug("Pushing {} to list {}".format(value, self.list_name))
            return self.redis.lpush(self.list_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return 0

    def trim(self, start, end):
        """
        Trim list to only contain elements in the range from start to end.
        :param start: starting index of range
        :param end: last index of range
        :return: String value indicating "OK" if operation was successful, otherwise None
        """
        try:
            app.logger.debug("Trimming list {} from {} to {}".format(self.list_name, start, end))
            return self.redis.ltrim(self.list_name, start, end)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def slice(self, start, end):
        """
        Return the elements in the list that are in the range from start to end.
        :param start: starting index of range
        :param end: last index of range
        :return: list of matching elements, if existent, otherwise empty list
        """
        try:
            app.logger.debug("Getting slice of list {} from {} to {}".format(self.list_name, start, end))
            return self.redis.lrange(self.list_name, start, end)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return []

    def length(self):
        """
        Returns length of list
        :return: int containing length of list
        """
        try:
            app.logger.debug("Getting length of list {}".format(self.list_name))
            return self.redis.llen(self.list_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None
