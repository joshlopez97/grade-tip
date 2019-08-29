from flask import current_app as app
from flask_login import current_user

from GradeTip.models.entries import get_time


class PostManager:
    def __init__(self, redis_manager):
        # TODO: Disable Anonymous posts
        self.redis = redis_manager

    @staticmethod
    def validate_post_data(post_data):
        for field in ["title", "description"]:
            value = post_data.get(field)
            if not isinstance(value, str) or len(value) == 0:
                app.logger.debug("Field {} cannot have value {}".format(field, value))
                return False
        return True

    @property
    def display_name(self):
        if current_user is not None and current_user.is_authenticated:
            return current_user.display_name
        return "Anon"

    def request_post(self, school_id, form_data):
        """ Request to create a post in a school's page. """
        if not self.validate_post_data(form_data):
            return False
        # get new request_id
        request_id = self.redis.get_new_id("request_id", "requests")
        if request_id is None:
            return False

        # store data into map with 'request/request_id' as the key
        identifier = "request/{}".format(request_id)
        return self.redis.store_hash(identifier, {
            "sid": school_id,
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": self.display_name,
            "time": get_time()
        })

    def create_post(self, request):
        """ Create a post for a school's page. """
        # get new post_id
        school_id = request["sid"]
        post_id = "p" + self.redis.get_new_id("post_ids/{}".format(school_id), "posts/{}".format(school_id))
        if post_id is None:
            return False

        # store data into map with 'sid/post_id' as the key
        identifier = "{}/{}".format(school_id, post_id)
        return self.redis.store_hash(identifier, {
            "title": request["title"],
            "description": request["description"],
            "uid": request["uid"],
            "time": request["time"],
            "requestType": "textpost"
        })

    def get_posts_from_school(self, school_id):
        """ Get all existing posts for school. """
        post_ids = self.redis.get_set("posts/{}".format(school_id))
        posts = {}
        for post_id in post_ids:
            posts[post_id] = self.redis.get_hash("{}/{}".format(school_id, post_id))
        app.logger.debug("fetched {} posts for sid {}".format(len(posts), school_id))
        return posts
