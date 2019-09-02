import traceback

from flask import current_app as app


class RedisValues:
    """ Wrapper class for handling Redis values. """
    def __init__(self, redis_server):
        self.redis_server = redis_server

    def get_new_id(self, id_source, id_destination):
        """ Grabs a new ID via the 'counter' value at id_source and
            stores it in the set at id_destination.
        """
        try:
            new_id = self.redis_server.get(id_source)
            if new_id is None:
                new_id = 0
            self.redis_server.incrby(id_source, 1)
            app.logger.debug("Retrieved new ID {} from key {}".format(new_id, id_source))
            self.redis_server.sadd(id_destination, new_id)
            app.logger.debug("Stored new ID {} in set at key {}".format(new_id, id_destination))
            return str(new_id)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def remove(self, key_name):
        try:
            self.redis_server.delete(key_name)
            app.logger.debug("Stored key {}".format(key_name))
            return True
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def get_value(self, key_name):
        try:
            value = self.redis_server.get(key_name)
            app.logger.debug("Retrieved {} from key {}".format(value, key_name))
            return value
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def set(self, key_name, value):
        try:
            return self.redis_server.setnx(key_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def set_expiring_value(self, key_name, value, ttl_in_seconds):
        try:
            self.set(key_name, value)
            self.redis_server.expire(key_name, ttl_in_seconds)
            return True
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def exists(self, key_name):
        try:
            return self.redis_server.exists(key_name)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False
