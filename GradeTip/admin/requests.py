from flask import current_app as app, jsonify, request

from GradeTip.admin.auth import validate_headers
from GradeTip.content.posts import create_post, delete_request
from GradeTip.models import redis_server


def fetch_post_requests():
    if not validate_headers(redis_server, request.headers):
        return jsonify({}), 404
    request_ids = redis_server.smembers("requests")
    requests = {}
    for request_id in request_ids:
        requests[request_id] = get_request(request_id)
    app.logger.debug("fetched {} requests".format(len(requests)))
    return jsonify(requests)


def get_request(request_id):
    return redis_server.hgetall("request/{}".format(request_id))


def approve_request(request_id):
    request_data = get_request(request_id)
    if request_data is not None:
        return jsonify({"result": create_post(redis_server, request_data)})
    return jsonify({"result": False})


def deny_request(request_id):
    return jsonify({"result": delete_request(redis_server, request_id)})
