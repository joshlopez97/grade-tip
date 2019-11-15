from flask import current_app as app

from GradeTip.content.content import ContentStore
from GradeTip.content.identifier import NameProvider
from GradeTip.redis.set import RedisSet


class TextPostStore(ContentStore):
    """
    Class manages user text posts on school pages.
    """

    def __init__(self, user_manager):
        super().__init__(["title", "description"], "textpost")
        self.user = user_manager
        self.name_provider = NameProvider()

    def request_post(self, school_id, form_data):
        """
        Request to create a post in a school's page.
        :param school_id: ID of school to make request
        :param form_data: raw form data submitted by user
        :return: request ID if successful, otherwise None
        """
        if not super().validate_data(form_data):
            return False
        # get new request_id
        request_id = self.name_provider.generate_request_id(super().user_email)
        if request_id is None:
            return False

        # store data
        return super().request_content(request_id, {
            "sid": school_id,
            "title": form_data["title"],
            "description": form_data["description"],
            "uid": super().display_name,
            "email": super().user_email
        })

    def create_post(self, request):
        """
        Create a post for a school's page. Request data is promoted to a text post with a new
        text post ID.
        :param request: dict containing request data to promote
        :return: post ID if successful, otherwise None
        """
        # get new post_id
        school_id = request["sid"]
        user_email = request["email"]
        post_id = self.name_provider.generate_post_id(user_email, school_id)

        return super().make_content(post_id, {
            "title": request["title"],
            "sid": school_id,
            "description": request["description"],
            "uid": request["uid"],
            "email": user_email,
            "time": request["time"]
        })

    def get_posts(self, school_id):
        """
        Get all existing posts for school.
        :param school_id: ID of school
        :return: dict containing all posts for school
        """
        posts = {}
        post_set_key = self.name_provider.set_names.post(school_id)
        for post_id in RedisSet(post_set_key).values():
            posts[post_id] = super().get_content(post_id)
        app.logger.debug("fetched {} posts for sid {}".format(len(posts), school_id))
        return posts
