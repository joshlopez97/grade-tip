from flask import current_app as app, jsonify, request


class RequestManager:
    def __init__(self, redis_manager, post_manager, upload_manager, listing_manager, auth_manager):
        self.redis = redis_manager
        self.post = post_manager
        self.upload = upload_manager
        self.listing = listing_manager
        self.auth = auth_manager

    def fetch_post_requests(self):
        if not self.auth.validate_headers(request.headers):
            return jsonify({}), 404
        request_ids = self.redis.get_set("requests")
        requests = {}
        for request_id in request_ids:
            request_data = self.get_request(request_id)
            if request_data.get("requestType") == "listing":
                request_data["preview"] = self.upload.get_preview_from_listing(request_data["upload_id"])
                del request_data["upload_id"]
            app.logger.debug("request: {}".format(request_data))
            requests[request_id] = request_data
        app.logger.debug("fetched {} requests".format(len(requests)))
        return jsonify(requests)

    def delete_request(self, request_id):
        app.logger.debug("deleting request with id: {}".format(request_id))
        id_deleted = self.redis.remove_from_set("requests", request_id)
        hash_deleted = self.redis.remove("request/{}".format(request_id))
        return id_deleted and hash_deleted

    def pop_request(self, request_id):
        request_data = self.get_request(request_id)
        self.delete_request(request_id)
        return request_data

    def get_request(self, request_id):
        app.logger.debug("fetching request with id: {}".format(request_id))
        return self.redis.get_hash("request/{}".format(request_id))

    def approve_request(self, request_id):
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
        app.logger.debug("denying request with id: {}".format(request_id))
        request_data = self.pop_request(request_id)
        if request_data is not None and request_data.get("requestType") == "listing":
            return jsonify({"result": self.redis.remove(request_data["upload_id"])})
        return jsonify({"result": False})
