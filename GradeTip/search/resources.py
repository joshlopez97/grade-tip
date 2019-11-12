from flask import jsonify, request

from GradeTip.search import document_search, school_search


def posts_query():
    """
    Endpoint for a query to all GradeTip content (posts and listings)
    :return: JSON list of results
    """
    query_str = request.args.get("query")
    results = document_search.search(query_str)
    return jsonify(results)


def school_query():
    """
    Endpoint for a query to all GradeTip schools
    :return: JSON list of results
    """
    query_str = request.args.get("query")
    results = school_search.search(query_str)
    return jsonify(results)
