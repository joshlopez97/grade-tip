from GradeTip.admin import admin_authenticator
from GradeTip.content.listing import ListingStore
from GradeTip.content.textpost import TextPostStore
from GradeTip.content.request import RequestStore
from GradeTip.content.upload import UploadStore
from GradeTip.indexer import indexer
from GradeTip.redis import redis_values
from GradeTip.schools import school_store
from GradeTip.user import user_manager

post_store = TextPostStore(user_manager)
upload_store = UploadStore(indexer)
listing_store = ListingStore(upload_store, school_store)
request_store = RequestStore(redis_values, post_store, upload_store, listing_store, admin_authenticator)
