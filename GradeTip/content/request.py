from flask import current_app as app, jsonify, request

from GradeTip.redis.hash import RedisHash
from GradeTip.redis.set import RedisSet


class RequestManager:
    """
    Class for managing request data. A request is created each time a user wants to submit
    content to GradeTip. Once that content is approved by moderators, the request is deleted and replaced
    by the corresponding content data type.
    """
    def __init__(self, redis_manager, post_manager, upload_manager, listing_manager, auth_manager):
        self.redis = redis_manager
        self.post = post_manager
        self.upload = upload_manager
        self.listing = listing_manager
        self.auth = auth_manager
        self.request_ids = RedisSet("requests")

    def get_all_requests(self):
        """
        Gets all requests submitted to GradeTip.
        :return: dict containing request_ids as keys and request data as values
        """
        if not self.auth.validate_headers(request.headers):
            return jsonify({}), 404
        requests = {}
        for request_id in self.request_ids.values():
            request_data = self.get_request(request_id)
            if request_data.get("requestType") == "listing":
                request_data["preview"] = self.upload.get_preview_from_listing(request_data["upload_id"])
                del request_data["upload_id"]
            app.logger.debug("request: {}".format(request_data))
            requests[request_id] = request_data
        app.logger.debug("fetched {} requests".format(len(requests)))
        return requests

    def delete_request(self, request_id):
        """
        Deletes request and relevant request data.
        :param request_id: ID of request to be deleted
        :return: boolean indicating success of operation
        """
        app.logger.debug("deleting request with id: {}".format(request_id))
        id_deleted = self.request_ids.remove(request_id)
        hash_deleted = self.redis.remove(request_id)
        return id_deleted and hash_deleted

    def pop_request(self, request_id):
        """
        Retrieves request with ID request_id and then deletes that request.
        :param request_id: ID of request to find
        :return: dict containing request data
        """
        request_data = self.get_request(request_id)
        self.delete_request(request_id)
        return request_data

    def get_request(self, request_id):
        """
        Retrieves request with ID request_id.
        :param request_id: ID of request to find
        :return: dict containing request data
        """
        app.logger.debug("fetching request with id: {}".format(request_id))
        request_data = RedisHash(request_id).to_dict()
        app.logger.debug("request id {} has data {}".format(request_id, request_data))
        return request_data

    def approve_request(self, request_id):
        """
        Deletes request and promotes request data to a public post.
        :param request_id:
        :return: JSON with result of operation
        """
        app.logger.debug("approving request with id: {}".format(request_id))
        request_data = self.pop_request(request_id)
        result = False
        if request_data is not None:
            if request_data.get("requestType") == "textpost":
                result = self.post.create_post(request_data)
            else:
                result = self.listing.create_listing(request_data)
        return jsonify({"result": result})

    def deny_request(self, request_id):
        """
        Deletes request and takes no further action
        :param request_id:
        :return: JSON with result of operation
        """
        app.logger.debug("denying request with id: {}".format(request_id))
        request_data = self.pop_request(request_id)
        if request_data is not None and request_data.get("requestType") == "listing":
            return jsonify({"result": self.redis.remove(request_data["upload_id"])})
        return jsonify({"result": False})
