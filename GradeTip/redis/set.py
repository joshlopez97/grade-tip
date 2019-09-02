import traceback

from GradeTip.redis import redis_server
from flask import current_app as app


class RedisSet:
    """ Wrapper class for interacting with Redis sets. """
    def __init__(self, set_name):
        self.redis = redis_server
        self.set_name = set_name

    def values(self):
        """
        Return all values in set
        :return: set containing all values found
        """
        try:
            app.logger.debug("Retrieving all values from set {}".format(self.set_name))
            return self.redis.smembers(self.set_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return set()

    def add(self, values):
        """
        Adds values to set
        :param values: list of values to add
        :return: int containing number of values added
        """
        try:
            app.logger.debug("Storing {} in set {}".format(values, self.set_name))
            return self.redis.sadd(self.set_name, *values)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return 0

    def remove(self, value):
        """
        Remove value from set
        :param value: value to remove from set
        :return: boolean indicating success of operation
        """
        try:
            app.logger.debug("Removing {} from set {}".format(value, self.set_name))
            return self.redis.srem(self.set_name, value) <= 0
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def exists(self, value):
        """
        Checks if value exists in set
        :param value: value to look for
        :return: boolean indicating whether value exists or not
        """
        try:
            app.logger.debug("Checking if {} exists in set {}".format(value, self.set_name))
            return self.redis.sismember(self.set_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False
