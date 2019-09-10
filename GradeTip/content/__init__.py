from GradeTip.admin import admin_authenticator
from GradeTip.content.listing import ListingManager
from GradeTip.content.textpost import TextPostManager
from GradeTip.content.request import RequestManager
from GradeTip.content.upload import UploadManager
from GradeTip.redis import redis_manager
from GradeTip.schools import school_manager
from GradeTip.user import user_manager

post_manager = TextPostManager(user_manager)
upload_manager = UploadManager()
listing_manager = ListingManager(upload_manager, school_manager, user_manager)
request_manager = RequestManager(redis_manager, post_manager, upload_manager, listing_manager, admin_authenticator)
