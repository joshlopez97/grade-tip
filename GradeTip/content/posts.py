import traceback

from flask_login import current_user
from flask import current_app as app

from GradeTip.content.redis import get_new_id, store_hash
from GradeTip.models.entries import get_time, formatTime


def validate_post_data(post_data):
    # TODO: Validate post data
    return True


def get_username():
    # TODO: Disable Anonymous user posts
    displayName = "Anonymous"
    if current_user.is_authenticated:
        displayName = current_user.display_name
    return displayName


def request_post(redis_server, school_id, form_data):
    """ Request to create a post in a school's page. """
    try:
        # get new request_id
        request_id = get_new_id(redis_server, "request_id", "requests")

        # store data into map with 'request/request_id' as the key
        username = get_username()
        identifier = "request/{}".format(request_id)
        store_hash(redis_server, identifier, {
            "sid": school_id,
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": username,
            "time": get_time()
        })
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(form_data)))
        app.logger.error(e)
        traceback.print_exc()
    return False


def create_post(redis_server, request):
    """ Create a post for a school's page. """
    try:
        school_id = request["sid"]
        # get new post_id
        post_id = get_new_id(redis_server, "post_ids/{}".format(school_id), "posts/{}".format(school_id))

        # store data into map with 'sid/post_id' as the key
        identifier = "{}/{}".format(school_id, post_id)
        store_hash(redis_server, identifier, {
            "title": request["title"],
            "description": request["description"],
            "uid": request["uid"],
            "time": request["time"],
            "requestType": "textpost"
        })
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(request)))
        app.logger.error(e)
        traceback.print_exc()
    return False


def get_posts_from_school(redis_server, school_id):
    """ Get all existing posts for school. """
    post_ids = redis_server.smembers("posts/{}".format(school_id))
    posts = {}
    for post_id in post_ids:
        posts[post_id] = redis_server.hgetall("{}/{}".format(school_id, post_id))
    app.logger.debug("fetched {} posts for sid {}".format(len(posts), school_id))
    return posts


def delete_request(redis_server, request_id):
    app.logger.info("deleting request with id: {}".format(request_id))
    id_deleted = redis_server.srem("requests", request_id) <= 0
    hash_deleted = redis_server.delete("request/{}".format(request_id)) <= 0

    if not id_deleted:
        app.logger.info("non-existent request id: {}".format(request_id))

    if not hash_deleted:
        app.logger.info("no data found for request with id: {}".format(id))

    return id_deleted and hash_deleted
