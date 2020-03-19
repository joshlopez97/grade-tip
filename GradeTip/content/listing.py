import traceback

from flask import current_app as app

from GradeTip.content.content import ContentStore
from GradeTip.content.identifier import NameProvider
from GradeTip.redis.set import RedisSet


class ListingStore(ContentStore):
    """
    Class manages listing data. Listings are posts that contain PDF uploads of documents
    that are uploaded for a specific course at a specific school. Each listing must be approved
    by moderators before being submitted.
    """
    def __init__(self, upload_manager, school_manager):
        super().__init__(["school", "title", "cid", "kind"], "listing")
        self.upload = upload_manager
        self.school = school_manager
        self.name_provider = NameProvider()

    def request_listing(self, form_data, file):
        """
        Request to create a listing in a school's page.
        :param form_data: raw form data submitted by user
        :param file: flask file object for uploaded PDF document
        :return: request ID if successful, otherwise None
        """
        if not super().validate_data(form_data):
            return False
        # get new request_id
        request_id = self.name_provider.generate_request_id(super().user_email)
        if request_id is None:
            return False

        # upload files
        upload_id = self.name_provider.generate_upload_id(request_id)
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
        :return: listing ID if successful, otherwise None
        """
        school_id = request["sid"]
        user_email = request["uid"]
        # get new listing_id
        listing_id = self.name_provider.generate_listing_id(user_email, school_id)

        # upload files
        new_upload_id = self.name_provider.generate_upload_id(listing_id)
        filepaths = self.upload.promote_uploads(request["upload_id"], new_upload_id)
        RedisSet(new_upload_id).add(filepaths)

        # store listing data in redis
        return super().make_content(listing_id, {
            "sid": school_id,
            "title": request["title"],
            "course": request["course"],
            "kind": request["kind"],
            "uid": user_email,
            "email": request["email"],
            "upload_id": new_upload_id,
            "time": request["time"]
        })

    def get_listing(self, listing_id):
        """
        Get listing data for listing with given ID
        :param listing_id: ID of listing to find
        :return: dict containing listing data
        """
        listing_data = super().get_content(listing_id)
        if not listing_data:
            raise ValueError("Listing with ID {} does not exist".format(listing_id))
        listing_data["preview"] = self.upload.get_preview_from_listing(listing_data["upload_id"])
        listing_data["id"] = listing_id
        app.logger.debug("fetched listing {}".format(listing_data))
        return listing_data

    def get_listings(self, school_id):
        """
        Get all existing listings for school.
        :param school_id: ID of school to get listings from
        :return: dict containing all listing data for school
        """
        listings = {}
        listing_set_key = self.name_provider.set_names.listing(school_id)
        for listing_id in RedisSet(listing_set_key).values():
            try:
                listings[listing_id] = self.get_listing(listing_id)
            except Exception as e:
                app.logger.error("failed to fetch listing with id {}\n{}", listing_id, str(e))
        app.logger.debug("fetched {} listings for sid {}".format(len(listings), school_id))
        return listings
