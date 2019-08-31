import traceback

from GradeTip.models import redis_server
from flask import current_app as app


class RedisDao:
    def __init__(self):
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

    def get_hash(self, hash_name):
        try:
            hash_data = self.redis_server.hgetall(hash_name)
            app.logger.debug("Retrieved {} from hash {}".format(hash_data, hash_name))
            return hash_data
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return {}

    def set_hash(self, hash_name, data):
        try:
            self.redis_server.hmset(hash_name, data)
            self.redis_server.bgsave()
            app.logger.debug("Stored {} in key {}".format(str(data), hash_name))
            return True
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def set_hash_value(self, hash_name, key_name, value):
        try:
            return self.redis_server.hset(hash_name, key_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def remove(self, key_name):
        try:
            self.redis_server.delete(key_name)
            app.logger.debug("Stored key {}".format(key_name))
            return True
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def get_from_hash(self, hash_name, key_name):
        try:
            value = self.redis_server.hget(hash_name, key_name)
            app.logger.debug("Retrieved {} from key {} in hash {}".format(value, key_name, hash_name))
            return value
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return None

    def get_set(self, set_name):
        try:
            set_data = self.redis_server.smembers(set_name)
            app.logger.debug("Retrieved {} from set {}".format(set_data, set_name))
            return set_data
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return []

    def remove_from_set(self, set_name, value):
        try:
            id_deleted = self.redis_server.srem(set_name, value) <= 0
            if id_deleted:
                app.logger.debug("Removed {} from set {}".format(value, set_name))
                return True
            app.logger.debug("No instance of {} found in set {}".format(value, set_name))
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def add_to_set(self, key_name, values):
        try:
            self.redis_server.sadd(key_name, *values)
            app.logger.debug("Stored {} in key {}".format(str(values), key_name))
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

    def set_value(self, key_name, value):
        try:
            return self.redis_server.setnx(key_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def set_expiring_value(self, key_name, value, ttl_in_seconds):
        try:
            self.set_value(key_name, value)
            self.redis_server.expire(key_name, ttl_in_seconds)
            return True
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False

    def exists_in_set(self, set_name, value):
        try:
            return self.redis_server.sismember(set_name, value)
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

    def exists_in_hash(self, hash_name, value):
        try:
            return self.redis_server.hexists(hash_name, value)
        except Exception as e:
            app.logger.error(e)
            traceback.print_exc()
        return False
