import uuid
import bcrypt
from flask import current_app as app
from flask_login import login_user, current_user
from GradeTip.models.users import User


def validate_login(login, password, redis_server):
    try:
        hashed = str.encode(redis_server.get("hash: {}".format(login)))
        return bcrypt.hashpw(str.encode(password), hashed) == hashed
    except Exception as e:
        app.logger.error(e)
        return False


def create_session(email, redis_server):
    """ Create a volatile Redis database entry with expiration time
    EXPIRE_TIME_SEC, create User object, and login User to Flask-Login.

    Args:
        email: string representation of username to create a session with.
        redis_server: instance of Strict Redis server
    """
    redis_server.setnx("usersession: {}".format(email), str(uuid.uuid4()))
    redis_server.expire('usersession: {}'.format(email), 4 * 60 * 60)
    redis_server.exists('usersession: {}'.format(email))
    user = User.get(email, redis_server)
    login_user(user, remember=True)


def get_session(username, redis_server):
    """ Return session id from Redis database.

    Args:
        username: string representation of username to return id of.
        redis_server: instance of Strict Redis server

    Returns:
        string representation of user id.
    """
    return redis_server.get('usersession: {}'.format(username))


def delete_session(redis_server):
    """ Delete current user session. Remove user from database.

    Args:
        redis_server: instance of Strict Redis server
    """

    redis_server.delete('usersession: {}'.format(current_user.id))
