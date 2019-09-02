from flask_login import UserMixin

from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class User(UserMixin):
    """ This object inherits from UserMixin class and keeps track of User
    session status.

    Attributes:
        username: string represention of a User's username
        session_id: string representation of a random generated session ID
    """

    def __init__(self, school, email, display_name, session_id):
        """ Inits User with username and session ID. """
        self.school = school
        self.id = email
        self.display_name = display_name
        self.session_id = session_id

    @property
    def is_authenticated(self):
        """ Initialized User is authenticated by default.

        Returns:
            A boolean indicating authentication status.
        """
        return True

    @property
    def is_active(self):
        """ Initialized User is active by default.

        Returns:
            A boolean indicating active status.
        """
        return True

    @property
    def is_anonymous(self):
        """ Initialized User is not anonymous by default.

        Returns:
            A boolean indicating if user is anonymous.
        """
        return False


class UserManager:
    def __init__(self, redis_manager):
        self.redis = redis_manager
        self.requests_prefix = "req/{}"
        self.emails = RedisSet('users')
        self.displayNames = RedisSet('displayNames')

    def create_user(self, email):
        session_id = self.redis.get_value("usersession: {}".format(email))
        user_data = RedisHash(email).to_dict()
        if session_id and user_data:
            return User(user_data['school'], email, user_data['displayName'], session_id)
        return None

    def store_user_in_redis(self, email, password_hash, school, display_name):
        self.emails.add(email)
        self.displayNames.add(display_name)
        user_data = {'school': school, 'displayName': display_name}
        RedisHash(email).update(user_data)
        self.redis.set("hash: {}".format(email), password_hash)

    def made_request(self, email, request_id):
        return RedisSet("req/{}".format(email)).add([request_id])

    def remove_request(self, email, request_id):
        return RedisSet("req/{}".format(email)).remove(request_id)

    def made_post(self, email, post_id):
        return RedisSet("posts/{}".format(email)).add([post_id])

    def get_requests(self, email):
        return RedisSet("req/{}".format(email)).values()

    def get_posts(self, email):
        return RedisSet("posts/{}".format(email)).values()
