import json
import random

from flask import request

from GradeTip import college_data, hsdata
from GradeTip.models import redis_server

with open("static/txt/nouns.txt", "r") as f:
    nouns = [line.strip('\n') for line in f if line.strip('\n')]
with open("static/txt/adjectives_names.txt", "r") as f:
    adjectives = [line.strip('\n') for line in f if line]


def getcolleges():
    return json.dumps(college_data)


def gethighschools():
    return json.dumps(hsdata)


def getusernames():
    usernames = []
    while len(usernames) < 50:
        un = random.choice(adjectives) + random.choice(nouns)
        if not redis_server.sismember('displayNames', un):
            usernames += [un]

    return json.dumps(usernames)


def mockdata():
    schools = [school for school in college_data.keys() if 'california' in school.lower()]
    to_return = {'schools': schools}
    return json.dumps(to_return)


def validate_email():
    email = request.form.get('email')
    return json.dumps(not redis_server.exists(email))

