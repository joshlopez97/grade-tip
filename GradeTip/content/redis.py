import traceback

from flask import current_app as app


def get_new_id(redis_server, id_source, id_destination):
    """ Grabs a new ID via the 'counter' value at id_source and
        stores it in the set at id_destination.
    """
    try:
        new_id = redis_server.get(id_source)
        if new_id is None:
            new_id = 0
        redis_server.incrby(id_source, 1)
        app.logger.debug("Retrieved new ID {} from key {}".format(new_id, id_source))
        redis_server.sadd(id_destination, new_id)
        app.logger.debug("Stored new ID {} in set at key {}".format(new_id, id_destination))
        return str(new_id)
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return None


def add_to_set(redis_server, key_name, values):
    try:
        redis_server.sadd(key_name, *values)
        app.logger.debug("Stored {} in key {}".format(str(values), key_name))
        return True
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return False


def store_hash(redis_server, hash_name, data):
    try:
        redis_server.hmset(hash_name, data)
        redis_server.bgsave()
        app.logger.debug("Stored {} in key {}".format(str(data), hash_name))
        return True
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return False


def remove(redis_server, key_name):
    try:
        redis_server.delete(key_name)
        app.logger.debug("Stored key {}".format(key_name))
        return True
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return False


def remove_from_set(redis_server, set_name, value):
    try:
        id_deleted = redis_server.srem(set_name, value) <= 0
        if id_deleted:
            app.logger.debug("Removed {} from set {}".format(value, set_name))
            return True
        app.logger.debug("No instance of {} found in set {}".format(value, set_name))
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return False


def get_from_hash(redis_server, hash_name, key_name):
    try:
        value = redis_server.hget(hash_name, key_name)
        app.logger.debug("Retrieved {} from key {} in hash {}".format(value, key_name, hash_name))
        return value
    except Exception as e:
        app.logger.error(e)
        traceback.print_exc()
    return None
