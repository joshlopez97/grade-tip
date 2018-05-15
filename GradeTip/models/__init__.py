import redis
import os

""" Initialize redis server. """
redis_server = redis.StrictRedis(host='localhost',
                                 port=6379,
                                 db=0, decode_responses=True)