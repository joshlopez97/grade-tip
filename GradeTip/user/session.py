import uuid

import bcrypt
from flask import current_app as app
from flask_login import login_user


class SessionManager:
    def __init__(self, redis_manager, user_factory):
        self.redis = redis_manager
        self.user = user_factory

    def validate_login(self, email, password):
        """
        Validate that user entry exists with email provided and that the provided
        password matches the hashed password for that user
        :param email: email of user
        :param password: password of user
        :return: boolean indicating result of validation
        """
        try:
            hashed = str.encode(self.redis.get_value("hash: {}".format(email)))
            return bcrypt.hashpw(str.encode(password), hashed) == hashed
        except Exception as e:
            app.logger.error(e)
        return False

    def create_session(self, email):
        """
        Creates new session for user with provided email
        :param email: email of user
        """
        self.redis.set_expiring("usersession: {}".format(email), str(uuid.uuid4()), 4 * 60 * 60)
        user = self.user.create_user(email)
        login_user(user, remember=True)

    def get_session_id(self, email):
        """
        Fetch session id for user with provided email
        :param email: email of user
        :return: string containing session id
        """
        return self.redis.get_value('usersession: {}'.format(email))

    def delete_session(self, email):
        """
        Delete active session for user with provided email
        :param email: email of user
        :return: boolean indicating result of operation
        """
        return self.redis.remove('usersession: {}'.format(email))
