import traceback

from flask import current_app as app
from flask_login import current_user

from GradeTip.content.identifier import IDGenerator
from GradeTip.content.utility import get_time
from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class ListingManager:
    def __init__(self, redis_manager, upload_manager, school_manager, user_manager):
        self.redis = redis_manager
        self.upload = upload_manager
        self.school = school_manager
        self.user = user_manager
        self.id_generator = IDGenerator()

    def request_listing(self, form_data, file):
        """ Request to create a listing in a school's page. """
        if not self.validate_listing_data(form_data):
            return False
        # get new request_id
        request_id = self.id_generator.generate("r-", self.user_email, "requests")
        if request_id is None:
            return False

        # upload files
        upload_id = "ur{}".format(request_id)
        filepaths, numPages = self.upload.add_file_to_listing(file, upload_id)
        if len(filepaths) == 0:
            app.logger.error("Error: no filepaths were created")
            return False
        if RedisSet(upload_id).add(filepaths) != len(filepaths):
            app.logger.error("Error: not all filepaths were added to set {}".format(upload_id))
            return False

        # store data into map with 'request/request_id' as the key
        identifier = "request/{}".format(request_id)
        self.user.made_request(self.user_email, identifier)

        return RedisHash(identifier).update({
            "sid": self.school.get_school_id(form_data["school"]),
            "title": form_data["title"],
            "course": form_data["cid"],
            "kind": form_data["kind"],
            "uid": self.display_name,
            "email": self.user_email,
            "upload_id": upload_id,
            "numPages": numPages,
            "time": get_time(),
            "requestId": request_id,
            "requestType": "listing"
        })

    def create_listing(self, request):
        """ Create a listing for a school's page. """
        school_id = request["sid"]
        # get new listing_id
        listing_id = "l{}".format(self.redis.get_new_id("listing_ids/{}".format(school_id),
                                                        "listings/{}".format(school_id)))

        # upload files
        new_upload_id = "u{}".format(listing_id)
        filepaths = self.upload.move_files_to_listing(request["upload_id"], new_upload_id)
        RedisSet(new_upload_id).add(filepaths)

        # store data into map with 'sid/listing_id' as the key
        identifier = "{}/{}".format(school_id, listing_id)
        self.user.made_post(request["email"], identifier)
        return RedisHash(identifier).update({
            "sid": school_id,
            "title": request["title"],
            "course": request["course"],
            "kind": request["kind"],
            "uid": request["uid"],
            "email": request["email"],
            "upload_id": new_upload_id,
            "time": request["time"],
            "postType": "listing"
        })

    def get_listings_from_school(self, school_id):
        """ Get all existing listings for school. """
        listing_ids = RedisSet("listings/{}".format(school_id)).values()
        listings = {}
        for listing_id in listing_ids:
            try:
                listing_data = RedisHash("{}/l{}".format(school_id, listing_id)).to_dict()
                listing_data["preview"] = self.upload.get_preview_from_listing(listing_data["upload_id"])
                del listing_data["upload_id"]
                listings[listing_id] = listing_data
                app.logger.debug("fetched listing {}".format(listing_data))
            except:
                app.logger.debug("failed to fetch listing with id {}".format(listing_id))
                traceback.print_exc()
        app.logger.debug("fetched {} listings for sid {}".format(len(listings), school_id))
        return listings

    @staticmethod
    def validate_listing_data(listing_data):
        for field in ["school", "title", "cid", "kind"]:
            value = listing_data.get(field)
            if not isinstance(value, str) or len(value) == 0:
                app.logger.debug("Field {} cannot have value {}".format(field, value))
                return False
        return True

    @property
    def display_name(self):
        if current_user is not None and current_user.is_authenticated:
            return current_user.display_name
        return "Anon"

    @property
    def user_email(self):
        if current_user is not None and current_user.is_authenticated:
            return current_user.id
        return "anon@anon.com"
