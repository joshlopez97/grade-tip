import traceback

from flask import current_app as app
from flask_login import current_user

from GradeTip.content.content import ContentManager
from GradeTip.content.identifier import IDGenerator
from GradeTip.content.utility import get_time
from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class ListingManager(ContentManager):
    """
    Class manages listing data. Listings are posts that contain PDF uploads of documents
    that are uploaded for a specific course at a specific school. Each listing must be approved
    by moderators before being submitted.
    """
    def __init__(self, upload_manager, school_manager):
        super().__init__(["school", "title", "cid", "kind"], "textpost")
        self.upload = upload_manager
        self.school = school_manager
        self.id_generator = IDGenerator()

    def request_listing(self, form_data, file):
        """
        Request to create a listing in a school's page.
        :param form_data: raw form data submitted by user
        :param file: flask file object for uploaded PDF document
        :return: boolean indicating success of operation
        """
        if not super().validate_data(form_data):
            return False
        # get new request_id
        request_id = self.id_generator.generate("r-", super().user_email, "requests")
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

        # store request data in redis
        return super().request_content(request_id, {
            "sid": self.school.get_school_id(form_data["school"]),
            "title": form_data["title"],
            "course": form_data["cid"],
            "kind": form_data["kind"],
            "uid": super().display_name,
            "email": super().user_email,
            "upload_id": upload_id,
            "numPages": numPages,
            "requestId": request_id
        })

    def create_listing(self, request):
        """
        Create a listing for a school's page.
        :param request: request data to promote to listing
        :return: boolean indicating success of operation
        """
        school_id = request["sid"]
        # get new listing_id
        listing_id = self.id_generator.generate("l-", super().user_email, "listings/{}".format(school_id))

        # upload files
        new_upload_id = "u{}".format(listing_id)
        filepaths = self.upload.move_files_to_listing(request["upload_id"], new_upload_id)
        RedisSet(new_upload_id).add(filepaths)

        # store listing data in redis
        identifier = "{}/{}".format(school_id, listing_id)
        return super().make_content(identifier, {
            "sid": school_id,
            "title": request["title"],
            "course": request["course"],
            "kind": request["kind"],
            "uid": request["uid"],
            "email": request["email"],
            "upload_id": new_upload_id,
            "time": request["time"]
        })

    def get_listings_from_school(self, school_id):
        """
        Get all existing listings for school.
        :param school_id: ID of school to get listings from
        :return: dict containing all listing data for school
        """
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
