from GradeTip.user.users import UserFactory
from GradeTip.redis import redis_manager
from GradeTip.user.sessions import SessionManager
from GradeTip.user.username import UsernameGenerator

user_factory = UserFactory(redis_manager)
session_manager = SessionManager(redis_manager, user_factory)
username_generator = UsernameGenerator(redis_manager)
