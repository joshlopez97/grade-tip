from flask_login import current_user


class ContentManager:
    """
    Class manages user text posts on school pages.
    """

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
