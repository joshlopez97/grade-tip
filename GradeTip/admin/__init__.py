from GradeTip.admin.AuthManager import AuthManager
from GradeTip.redis import redis_manager

auth_manager = AuthManager(redis_manager)
