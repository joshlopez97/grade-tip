from flask import current_app as app
from flask_login import current_user

from GradeTip.content.identifier import IDGenerator
from GradeTip.content.utility import get_time
from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class TextPostManager:
    """
    Class manages user text posts on school pages.
    """
    def __init__(self, user_manager):
        self.user = user_manager
        self.id_generator = IDGenerator()

    def request_post(self, school_id, form_data):
        """
        Request to create a post in a school's page.
        :param school_id: ID of school to make request
        :param form_data: raw form data submitted by user
        :return: boolean indicating success of operation
        """
        if not self.validate_post_data(form_data):
            return False
        # get new request_id
        request_id = self.id_generator.generate("r-", self.user_email, "requests")
        if request_id is None:
            return False

        # store data into map with 'request/request_id' as the key
        identifier = "request/{}".format(request_id)
        self.user.made_request(self.user_email, identifier)
        return RedisHash(identifier).update({
            "sid": school_id,
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": self.display_name,
            "email": self.user_email,
            "time": get_time()
        })

    def create_post(self, request):
        """
        Create a post for a school's page. The incoming data is in the form of a post request.
        :param request: dict containing request data to promote
        :return: boolean indicating whether or not post was created.
        """
        # get new post_id
        school_id = request["sid"]
        post_id = self.id_generator.generate("p-", self.user_email, "posts/{}".format(school_id))

        # store data into map with 'sid/post_id' as the key
        identifier = "{}/{}".format(school_id, post_id)
        self.user.made_post(request["email"], identifier)
        return RedisHash(identifier).update({
            "title": request["title"],
            "description": request["description"],
            "uid": request["uid"],
            "email": request["email"],
            "time": request["time"],
            "requestType": "textpost"
        })

    def get_posts_from_school(self, school_id):
        """
        Get all existing posts for school.
        :param school_id: ID of school
        :return: dict containing all posts for school
        """
        posts = {}
        for post_id in RedisSet("posts/{}".format(school_id)).values():
            posts[post_id] = RedisHash("{}/{}".format(school_id, post_id)).to_dict()
        app.logger.debug("fetched {} posts for sid {}".format(len(posts), school_id))
        return posts

    @property
    def display_name(self):
        """
        Gets display name of current user
        """
        if current_user is not None and current_user.is_authenticated:
            return current_user.display_name
        return "Anon"

    @property
    def user_email(self):
        """
        Gets email of current user
        """
        if current_user is not None and current_user.is_authenticated:
            return current_user.id
        return "anon@anon.com"

    @staticmethod
    def validate_post_data(post_data):
        """
        Validates post data meets requirements
        :param post_data: dict containing post data
        :return: boolean indicating result of validation
        """
        for field in ["title", "description"]:
            value = post_data.get(field)
            if not isinstance(value, str) or len(value) == 0 or len(value) > 2000:
                app.logger.debug("Field {} cannot have value {}".format(field, value))
                return False
        return True
