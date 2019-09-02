import json

from flask import request, jsonify

from GradeTip.content import post_manager, listing_manager, request_manager


def posts_by_sid():
    """
    Endpoint to get all posts for a school.
    :return: JSON containing all post data for school
    """
    sid = request.form.get('sid')
    posts = post_manager.get_posts_from_school(sid)
    listings = listing_manager.get_listings_from_school(sid)
    posts.update(listings)
    return json.dumps(posts)


def approve_request(request_id):
    """
    Approves post request
    :param request_id: ID of request to approve
    :return: JSON containing result of operation
    """
    return request_manager.approve_request(request_id)


def deny_request(request_id):
    """
    Denies post request
    :param request_id: ID of request to deny
    :return: JSON containing result of operation
    """
    return request_manager.deny_request(request_id)


def fetch_post_requests():
    """
    Get all requests made total.
    :return: JSON containing all request data.
    """
    return jsonify(request_manager.get_all_requests())
