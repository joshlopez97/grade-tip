import json
from flask import request

from GradeTip.redis import redis_values
from GradeTip.user import username_generator


def usernames():
    return json.dumps(username_generator.get_usernames_in_bulk(50))


def validate_email():
    email = request.form.get('email')
    if email is None:
        return json.dumps(False)
    return json.dumps(not redis_values.exists(email))
