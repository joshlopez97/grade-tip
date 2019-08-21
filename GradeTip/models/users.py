import redis
from flask_login import UserMixin


class User(UserMixin):
    """ This object inherits from UserMixin class and keeps track of User
    session status.

    Attributes:
        username: string represention of a User's username
        session_id: string representation of a random generated session ID
    """

    def __init__(self, school, email, displayName, session_id):
        """ Inits User with username and session ID. """
        self.school = school
        self.id = email
        self.displayName = displayName
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

    @classmethod
    def get(cls, email, redis_server):
        """ Return a User session if session has not expired.

        Args:
            username: string representation of User's username.
            redis_server: instance of Strict Redis server
        """
        session_id = redis_server.get("usersession: {}".format(email))
        user_data = redis_server.hgetall(email)
        if session_id and user_data:
            return User(user_data['school'], email, user_data['displayName'], session_id)

def create_user(redis_server, email, passwordHash, school, displayName):
    redis_server.sadd('users', email)
    redis_server.sadd('displayNames', displayName)
    user_data = {}
    user_data['school'] = school
    user_data['displayName'] = displayName
    redis_server.hmset(email, user_data)
    redis_server.setnx("hash: {}".format(email), passwordHash)
