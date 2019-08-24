from flask_login import current_user
from flask import current_app as app

from GradeTip.models.entries import get_time, formatTime


def validate_post_data(post_data):
    return True


def create_post(redis_server, sid, form_data):
    try:
        # get new pid from key 'posts/sid' set
        pid = redis_server.scard("posts/{}".format(sid))

        # add new pid to set
        redis_server.sadd("posts/{}".format(sid), pid)

        displayName = "Anonymous"
        if current_user.is_authenticated:
            displayName = current_user.displayName

        # create dict with relevant post data
        post_data = {
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": displayName,
            "time": get_time()
        }

        # store data into map with 'sid/pid' as the key
        identifier = "{}/{}".format(sid, pid)
        redis_server.hmset(identifier, post_data)
        redis_server.bgsave()
        app.logger.debug("Stored {} in key {}".format(str(post_data), identifier))
        return True
    except Exception as e:
        print(e)
    return False


def get_posts_from_school(redis_server, sid):
    pids = redis_server.smembers("posts/{}".format(sid))
    posts = {}
    for pid in pids:
        print(pid)
        posts[pid] = redis_server.hgetall("{}/{}".format(sid, pid))
        print(posts[pid])
    app.logger.debug("fetched {} posts for sid {}".format(len(posts), sid))
    return posts
