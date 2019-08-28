from GradeTip.models.users import User
from flask import current_app as app


class AdminAuthenticator:
    def __init__(self, redis_manager):
        self.redis = redis_manager

    def is_admin(self, user):
        return user.is_authenticated and user.id == "joshlopez97@gmail.com"

    def validate_headers(self, headers):
        email = headers.get("email")
        sessionID = headers.get("sessionID")
        if email and sessionID:
            user = User.get(email)
            if user is None:
                app.logger.debug("User with email {} not found".format(email))
                return False
            return self.is_admin(user) and user.session_id == sessionID
        app.logger.debug("Missing headers email and/or sessionID")
        return False
