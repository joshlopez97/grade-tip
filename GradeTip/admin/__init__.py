from GradeTip.admin.AdminAuthenticator import AdminAuthenticator
from GradeTip.redis import redis_manager

admin_authenticator = AdminAuthenticator(redis_manager)
