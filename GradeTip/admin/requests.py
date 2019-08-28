from flask import current_app as app, jsonify, request

from GradeTip.admin.auth import validate_headers
from GradeTip.content.listings import create_listing
from GradeTip.content.posts import create_post
from GradeTip.content.redis import remove_from_set, remove
from GradeTip.content.uploads import get_preview_from_listing
from GradeTip.models import redis_server


def fetch_post_requests():
    if not validate_headers(redis_server, request.headers):
        return jsonify({}), 404
    request_ids = redis_server.smembers("requests")
    requests = {}
    for request_id in request_ids:
        request_data = get_request(request_id)
        if request_data.get("requestType") == "listing":
            request_data["preview"] = get_preview_from_listing(request_data["upload_id"])
            del request_data["upload_id"]
        app.logger.debug("request: {}".format(request_data))
        requests[request_id] = request_data
    app.logger.debug("fetched {} requests".format(len(requests)))
    return jsonify(requests)


def delete_request(request_id):
    app.logger.debug("deleting request with id: {}".format(request_id))
    id_deleted = remove_from_set(redis_server, "requests", request_id)
    hash_deleted = remove(redis_server, "request/{}".format(request_id))
    return id_deleted and hash_deleted


def pop_request(request_id):
    request_data = get_request(request_id)
    delete_request(request_id)
    return request_data


def get_request(request_id):
    app.logger.debug("fetching request with id: {}".format(request_id))
    return redis_server.hgetall("request/{}".format(request_id))


def approve_request(request_id):
    app.logger.debug("approving request with id: {}".format(request_id))
    request_data = pop_request(request_id)
    result = False
    if request_data is not None:
        if request_data["requestType"] == "textpost":
            result = create_post(redis_server, request_data)
        else:
            result = create_listing(redis_server, request_data)
    return jsonify({"result": result})


def deny_request(request_id):
    app.logger.debug("denying request with id: {}".format(request_id))
    request_data = pop_request(request_id)
    if request_data is not None and request_data["requestType"] == "listing":
        return jsonify({"result": remove(redis_server, request_data["upload_id"])})
    return jsonify({"result": False})
