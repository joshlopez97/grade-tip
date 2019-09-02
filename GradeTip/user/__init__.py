from GradeTip.user.user import UserManager
from GradeTip.redis import redis_manager
from GradeTip.user.session import SessionManager
from GradeTip.user.username import UsernameGenerator

user_manager = UserManager(redis_manager)
session_manager = SessionManager(redis_manager, user_manager)
username_generator = UsernameGenerator()
