from GradeTip.admin import auth_manager
from GradeTip.content.ListingManager import ListingManager
from GradeTip.content.PostManager import PostManager
from GradeTip.content.RequestManager import RequestManager
from GradeTip.content.UploadManager import UploadManager
from GradeTip.redis import redis_manager

post_manager = PostManager(redis_manager)
upload_manager = UploadManager()
listing_manager = ListingManager(redis_manager, upload_manager)
request_manager = RequestManager(redis_manager, post_manager, upload_manager, listing_manager, auth_manager)
