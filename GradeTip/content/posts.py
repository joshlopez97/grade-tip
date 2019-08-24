from flask_login import current_user
from flask import current_app as app

from GradeTip.models.entries import get_time, formatTime


def validate_post_data(post_data):
    # TODO: Validate post data
    return True


def get_username():
    # TODO: Disable Anonymous user posts
    displayName = "Anonymous"
    if current_user.is_authenticated:
        displayName = current_user.displayName
    return displayName


def request_post(redis_server, school_id, form_data):
    """ Request to create a post in a school's page. """
    try:
        # get new request_id from key 'requests' set
        request_id = redis_server.scard("requests".format(school_id))

        # add new request_id to set
        redis_server.sadd("requests".format(school_id), request_id)

        username = get_username()

        # create dict with relevant request data
        post_data = {
            "sid": school_id,
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": username,
            "time": get_time()
        }

        # store data into map with 'request/request_id' as the key
        identifier = "request/{}".format(request_id)
        redis_server.hmset(identifier, post_data)
        redis_server.bgsave()
        app.logger.debug("Stored {} in key {}".format(str(post_data), identifier))
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(form_data)))
        app.logger.error(e)
    return False


def create_post(redis_server, request):
    """ Create a post for a school's page. """
    try:
        school_id = request["sid"]
        # get new post_id from key 'posts/sid' set
        post_id = redis_server.scard("posts/{}".format(school_id))

        # add new post_id to set
        redis_server.sadd("posts/{}".format(school_id), post_id)

        # create dict with relevant post data
        post_data = {
            "title": request["title"],
            "description": request["description"],
            "uid": request["uid"],
            "time": request["time"]
        }

        # store data into map with 'sid/post_id' as the key
        identifier = "{}/{}".format(school_id, post_id)
        redis_server.hmset(identifier, post_data)
        redis_server.bgsave()
        app.logger.debug("Stored {} in key {}".format(str(post_data), identifier))
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(request)))
        app.logger.error(e)
    return False


def get_posts_from_school(redis_server, school_id):
    """ Get all existing posts for school. """
    post_ids = redis_server.smembers("posts/{}".format(school_id))
    posts = {}
    for post_id in post_ids:
        posts[post_id] = redis_server.hgetall("{}/{}".format(school_id, post_id))
    app.logger.debug("fetched {} posts for sid {}".format(len(posts), school_id))
    return posts
