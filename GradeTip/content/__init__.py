from GradeTip.admin import admin_authenticator
from GradeTip.content.ListingManager import ListingManager
from GradeTip.content.PostManager import PostManager
from GradeTip.content.RequestManager import RequestManager
from GradeTip.content.UploadManager import UploadManager
from GradeTip.redis import redis_manager
from GradeTip.schools import school_manager

post_manager = PostManager(redis_manager)
upload_manager = UploadManager()
listing_manager = ListingManager(redis_manager, upload_manager, school_manager)
request_manager = RequestManager(redis_manager, post_manager, upload_manager, listing_manager, admin_authenticator)
