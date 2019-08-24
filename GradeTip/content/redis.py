def get_new_id(redis_server, key_name):
    new_id = redis_server.get(key_name)
    if new_id is None:
        new_id = 0
    redis_server.incrby(key_name, 1)
    print("new_id = {}".format(new_id))
    print(type(new_id))
    return str(new_id)
