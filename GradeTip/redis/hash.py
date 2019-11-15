import traceback

from GradeTip.redis import redis_server
from flask import current_app as app


class RedisHash:
    """ Wrapper class for interacting with Redis hashes. """

    def __init__(self, hash_name):
        self.redis = redis_server
        self.hash_name = hash_name

    def to_dict(self):
        """
        Return hash data that is found at self.hash_name
        :return: dict containing all values in hash
        """
        try:
            app.logger.debug("Getting all data in hash {}".format(self.hash_name))
            return self.redis.hgetall(self.hash_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return {}

    def update(self, new_data):
        """
        Update hash with new_data, overriding existing keys if needed.
        :param new_data: dict containing new data to add to hash
        :return: string "OK" if operation is successful, otherwise None
        """
        try:
            app.logger.debug("Updating hash {} with {}".format(self.hash_name, new_data))
            return self.redis.hmset(self.hash_name, new_data)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def set(self, key, value):
        """
        Update hash with (key, value) pair, overriding existing key if needed.
        :param key: name of key to place value within hash
        :param value: value to set at key
        :return: string "OK" if operation is successful, otherwise None
        """
        try:
            app.logger.debug("Updating hash {} with ({}, {})".format(self.hash_name, key, value))
            return self.redis.hset(self.hash_name, key, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def get(self, key):
        """
        Get value at key within hash.
        :param key: name of key to look for value
        :return: value at key, if found, otherwise None
        """
        try:
            app.logger.debug("Getting key {} in hash {}".format(key, self.hash_name))
            return self.redis.hget(self.hash_name, key)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def exists(self, key=None):
        """
        Check if key exists in hash. If key is not provided, check if hash exists
        :param key: Name of key to look for
        :return: boolean indicating if key exists
        """
        try:
            if key is not None:
                app.logger.debug("Checking if key {} exists in hash {}".format(key, self.hash_name))
                return self.redis.hexists(self.hash_name, key)
            else:
                app.logger.debug("Checking if hash {} exists", self.hash_name)
                return self.redis.exists(self.hash_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def delete(self, key):
        """
        Deletes key from hash.
        :param key: Name of key to delete
        :return: boolean indicating if key was deleted
        """
        try:
            app.logger.debug("Deleting key {} from hash {}".format(key, self.hash_name))
            return self.redis.hdel(self.hash_name, key)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False
