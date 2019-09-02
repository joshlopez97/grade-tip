from flask import current_app as app

from GradeTip.user import user_manager


class AdminAuthenticator:
    @staticmethod
    def is_admin(user):
        """
        Checks is user is an admin account
        :param user: Flask user object to check
        :return: boolean indicating whether user is authenticated and id matches admin acct
        """
        return user.is_authenticated and user.id == app.config.get('ADMIN')

    def validate_headers(self, headers):
        """
        Validates request headers contain user email and sessionID for accessing
        privileged admin endpoints.
        :param headers: http headers to check
        :return: boolean indicating validation result
        """
        email = headers.get("email")
        sessionID = headers.get("sessionID")
        if email and sessionID:
            user = user_manager.create_user(email)
            if user is None:
                app.logger.debug("User with email {} not found".format(email))
                return False
            return self.is_admin(user) and user.session_id == sessionID
        app.logger.debug("Missing headers email and/or sessionID")
        return False
