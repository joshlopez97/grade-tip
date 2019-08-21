import time
from GradeTip.models.entries import get_time, formatTime

def new(redis_server, sid, title, body, cid="", price=""):
    """ Create a new hash entry with key value name in Redis. Initialize
    attributes and add new name in ENTRIES set in Redis.
    """

    # redis: add ID to set called "entries"
    pid = redis_server.scard("posts/{}".format(sid))
    redis_server.sadd("posts/{}".format(sid), pid)

    # create python dictionary for all assignment info
    info = {}
    info["title"] = title
    info["body"] = body
    info["cid"] = cid
    info["uid"] = current_user.displayName
    info["time"] = get_time()

    # redis: store dictionary into (sid, pid) identifier
    identifier = "{}/{}".format(sid, pid)
    redis_server.hmset(identifier, info)

    return True

def get_posts_from_school(redis_server, sid):
    pids = redis_server.smembers("posts/{}".format(sid))
    posts = {}
    for pid in pids:
        posts[pid] = redis_server.hgetall("{}/{}".format(sid, pid))
        posts[pid]["time"] = formatTime(posts[pid]["time"])

    return posts