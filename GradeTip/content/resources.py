import json

from flask import request, jsonify

from GradeTip.content import post_store, listing_store, request_store, reply_store


def posts_by_sid():
    """
    Endpoint to get all posts for a school.
    :return: JSON containing all post data for school
    """
    sid = request.form.get('sid')
    posts = post_store.get_posts(sid)
    listings = listing_store.get_liinstings(sid)
    posts.update(listings)
    return json.dumps(posts)


def replies_by_content_id():
    """
    Endpoint to get all replies for content with given ID.
    :return: JSON containing all reply data for content
    """
    content_id = request.args.get("content_id")
    replies = reply_store.get_replies(content_id)
    return json.dumps(replies)


def approve_request(request_id):
    """
    Approves post request
    :param request_id: ID of request to approve
    :return: JSON containing result of operation
    """
    return request_store.approve_request(request_id)


def deny_request(request_id):
    """
    Denies post request
    :param request_id: ID of request to deny
    :return: JSON containing result of operation
    """
    return request_store.deny_request(request_id)


def fetch_post_requests():
    """
    Get all requests made total.
    :return: JSON containing all request data.
    """
    return jsonify(request_store.get_all_requests())
