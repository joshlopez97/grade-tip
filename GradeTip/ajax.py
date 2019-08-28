import json
import os
import random
import re
from pathlib import Path

from flask import request
from pdf2image import convert_from_bytes

from GradeTip import college_data, hsdata
from GradeTip.content.listings import get_listings_from_school
from GradeTip.content.posts import (get_posts_from_school)
from GradeTip.models import redis_server
from GradeTip.models.entries import (get_comments, add_comment, dislike_comment,
                                     like_comment, nullify_comment)

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


def posts_by_sid():
    sid = request.form.get('sid')
    posts = get_posts_from_school(redis_server, sid)
    listings = get_listings_from_school(redis_server, sid)
    posts.update(listings)
    return json.dumps(posts)


def mockdata():
    schools = [school for school in college_data.keys() if 'california' in school.lower()]
    to_return = {'schools': schools}
    return json.dumps(to_return)


def validate_email():
    email = request.form.get('email')
    return json.dumps(not redis_server.exists(email))


def addcomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    comment = request.form['comment']
    add_comment(ID, comment, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))


def likecomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    like_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))


def dislikecomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    dislike_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))


def nullifycomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    nullify_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))


def toimages():
    # convert pdf to images
    file = request.files.get('file')
    print(file)
    imgs = convert_from_bytes(file.stream.read())
    paths = []

    # create random cache for images
    dr = os.path.join('static', 'tmp', str(random.randint(1, 10000)))
    while Path(dr).exists():
        dr = os.path.join('static', 'tmp', str(random.randint(1, 10000)))
    os.makedirs(dr)

    # store in cache
    for i, img in enumerate(imgs):
        path = dr + '/' + str(i) + '.png'
        img.save(path)
        paths += [path]

    return json.dumps({'paths': paths})
