from flask import current_app as app, jsonify

from GradeTip.content.posts import create_post
from GradeTip.models import redis_server


def fetch_post_requests():
    request_ids = redis_server.smembers("requests")
    requests = {}
    for request_id in request_ids:
        requests[request_id] = redis_server.hgetall("request/{}".format(request_id))
    app.logger.debug("fetched {} requests".format(len(requests)))
    return jsonify(requests)


def approve_request(request):
    if create_post(redis_server, request):
        return jsonify({"created": True})
    return jsonify({"created": False})

