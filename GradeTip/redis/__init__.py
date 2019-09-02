import redis

from GradeTip.redis.value import RedisValues

redis_server = redis.StrictRedis(host='localhost',
                                 port=6379,
                                 db=0, decode_responses=True)
redis_manager = RedisValues(redis_server)
