from flask import current_app as app
from flask_login import current_user

from GradeTip.content.utility import get_time
from GradeTip.redis.hash import RedisHash
from GradeTip.user import user_manager


class ContentStore:
    """
    Class manages user text posts on school pages.
    """
    def __init__(self, fields, content_type):
        self.fields = fields
        self.type = content_type

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

    def validate_data(self, post_data):
        """
        Validates that required fields are non-empty and underneath the content length limit
        :param post_data: dict containing post data
        :return: boolean indicating result of validation
        """
        for field in self.fields:
            value = post_data.get(field)
            if not isinstance(value, str) or len(value) == 0 or len(value) > 2000:
                app.logger.debug("Field {} cannot have value {}".format(field, value))
                return False
        return True

    def make_content(self, identifier, data):
        """
        Creates new redis hash with specified data representing some type of user-created content.
        :param identifier: string identifier for hash in redis
        :param data: content data
        :return: string identifier if operation is successful, otherwise None
        """
        user_manager.created_content(data["email"], identifier)
        data.update({"postType": self.type})
        app.logger.debug("Storing {} in {}".format(data, identifier))
        if RedisHash(identifier).update(data) is not None:
            return identifier

    @staticmethod
    def get_content(content_id):
        """
        Get content data for content with given ID
        :param content_id: ID of content
        :return: dict containing content data
        """
        return RedisHash(content_id).to_dict()

    def request_content(self, identifier, data):
        """
        Creates new redis hash with specified data representing a user request to create content.
        :param identifier: string identifier for hash in redis
        :param data: request data
        :return: string identifier if operation is successful, otherwise None
        """
        user_manager.created_content(data["email"], identifier)
        data.update({"requestType": self.type, "time": get_time()})
        app.logger.debug("Storing {} in {}".format(data, identifier))
        if RedisHash(identifier).update(data) is not None:
            return identifier
