from GradeTip.admin.auth import AdminAuthenticator
from GradeTip.redis import redis_manager

admin_authenticator = AdminAuthenticator(redis_manager)
