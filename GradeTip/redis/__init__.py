import redis

from GradeTip.redis.dao import RedisDao

redis_server = redis.StrictRedis(host='localhost',
                                 port=6379,
                                 db=0, decode_responses=True)
redis_manager = RedisDao(redis_server)
