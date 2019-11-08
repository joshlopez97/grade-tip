from GradeTip.user.user import UserManager
from GradeTip.redis import redis_values
from GradeTip.user.session import SessionManager
from GradeTip.user.username import UsernameGenerator

user_manager = UserManager(redis_values)
session_manager = SessionManager(redis_values, user_manager)
username_generator = UsernameGenerator()
