import traceback

from flask_login import current_user
from flask import current_app as app

from GradeTip.content.redis import get_new_id, store_hash, add_to_set
from GradeTip.content.uploads import add_file_to_listing, move_files_to_listing, get_preview_from_listing
from GradeTip.models.entries import get_time, formatTime
from GradeTip.schools.schools import get_school_id


def validate_listing_data(listing_data):
    for field in ["school", "title", "cid", "kind"]:
        value = listing_data.get(field)
        if not isinstance(value, str) or len(value) == 0:
            app.logger.debug("Field {} cannot have value {}".format(field, value))
            return False
    return True


def get_username():
    # TODO: Disable Anonymous user listings
    displayName = "Anonymous"
    if current_user.is_authenticated:
        displayName = current_user.display_name
    return displayName


def request_listing(redis_server, form_data, file):
    """ Request to create a listing in a school's page. """
    try:
        if not validate_listing_data(form_data):
            return False
        # get new request_id
        request_id = get_new_id(redis_server, "request_id", "requests")

        # upload files
        upload_id = "ur{}".format(request_id)
        filepaths = add_file_to_listing(file, upload_id)
        add_to_set(redis_server, upload_id, filepaths)

        # store data into map with 'request/request_id' as the key
        username = get_username()
        identifier = "request/{}".format(request_id)
        store_hash(redis_server, identifier, {
            "sid": get_school_id(form_data["school"]),
            "title": form_data["title"],
            "course": form_data["cid"],
            "kind": form_data["kind"],
            "uid": username,
            "upload_id": upload_id,
            "time": get_time(),
            "requestId": request_id,
            "requestType": "listing"
        })
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(form_data)))
        app.logger.error(e)
        traceback.print_exc()
    return False


def create_listing(redis_server, request_data):
    """ Create a listing for a school's page. """
    try:
        school_id = request_data["sid"]
        # get new listing_id
        listing_id = "l" + get_new_id(redis_server, "listing_ids/{}".format(school_id), "listings/{}".format(school_id))

        # upload files
        new_upload_id = "u{}".format(listing_id)
        filepaths = move_files_to_listing(request_data["upload_id"], new_upload_id)
        add_to_set(redis_server, new_upload_id, filepaths)

        # store data into map with 'sid/listing_id' as the key
        identifier = "{}/{}".format(school_id, listing_id)
        store_hash(redis_server, identifier, {
            "sid": school_id,
            "title": request_data["title"],
            "course": request_data["course"],
            "kind": request_data["kind"],
            "uid": request_data["uid"],
            "upload_id": new_upload_id,
            "time": request_data["time"],
            "postType": "listing"
        })
        return True
    except Exception as e:
        app.logger.error("Something went wrong trying to store {} in Redis".format(str(request_data)))
        app.logger.error(e)
        traceback.print_exc()
    return False


def get_listings_from_school(redis_server, school_id):
    """ Get all existing listings for school. """
    listing_ids = redis_server.smembers("listings/{}".format(school_id))
    listings = {}
    for listing_id in listing_ids:
        listing_data = redis_server.hgetall("{}/{}".format(school_id, listing_id))
        listing_data["preview"] = get_preview_from_listing(listing_data["upload_id"])
        del listing_data["upload_id"]
        listings[listing_id] = listing_data
        app.logger.debug("fetched listing {}".format(listing_data))
    app.logger.debug("fetched {} listings for sid {}".format(len(listings), school_id))
    return listings


def delete_request(redis_server, request_id):
    app.logger.info("deleting request with id: {}".format(request_id))
    id_deleted = redis_server.srem("requests", request_id) <= 0
    hash_deleted = redis_server.delete("request/{}".format(request_id)) <= 0

    if not id_deleted:
        app.logger.info("non-existent request id: {}".format(request_id))

    if not hash_deleted:
        app.logger.info("no data found for request with id: {}".format(id))

    return id_deleted and hash_deleted
