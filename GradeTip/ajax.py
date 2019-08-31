import json

from flask import request

from GradeTip.redis import redis_manager
from GradeTip.schools import school_manager
from GradeTip.user import username_generator


def colleges():
    return json.dumps(school_manager.get_college_data())


def usernames():
    return json.dumps(username_generator.get_usernames_in_bulk(50))


def validate_email():
    email = request.form.get('email')
    if email is None:
        return json.dumps(False)
    return json.dumps(not redis_manager.exists(email))

