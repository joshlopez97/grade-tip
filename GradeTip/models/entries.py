from flask import url_for
from flask_login import current_user
from PIL import Image, ImageFilter
import ast
import os
import re
import time
import json
from datetime import datetime, timedelta
from uuid import uuid4
from GradeTip import college_data
from GradeTip.config.redis import post

timeunits = ['year', 'month', 'day', 'hour', 'minute', 'second', 'second']


def create_entry(school, course, kind, name, redis_server):
    """ Create a new hash entry with key value name in Redis. Initialize
    attributes and add new name in ENTRIES set in Redis.
    """

    # redis: add ID to set called "entries"
    sid = college_data[school]['sid']
    pid = redis_server.scard("entries/{}".format(sid))
    redis_server.sadd("entries/{}".format(sid), pid)

    # create python dictionary for all assignment info
    info = {}
    info[post.sid] = school
    info[post.cid] = course
    info[post.uid] = "user"  # current_user.displayName
    info[post.kind] = kind
    info[post.title] = name
    info[post.time] = time.strftime(post.time_format, time.localtime())

    # redis: store dictionary into (sid, pid) identifier
    identifier = "{}/{}".format(sid, pid)
    redis_server.hmset(identifier, info)
    redis_server.expire(identifier, post.ex)

    ID = uuid4()
    while redis_server.hexists("ondeck", ID):
        ID = uuid4()

    redis_server.set(ID, identifier, ex=post.ex)

    # save in background
    redis_server.bgsave()

    return ID


def get_matching_entries(query, redis_server):
    terms = query.split(' ')
    results1 = []
    results2 = []
    try:
        for entryid in redis_server.smembers('entries'):
            if all(t.lower() in redis_server.hget(entryid, "name").lower() for t in terms):
                results1 += [get_result_entry_data(entryid, redis_server)]
            elif any(t.lower() in redis_server.hget(entryid, "name").lower() for t in terms):
                results2 += [get_result_entry_data(entryid, redis_server)]
    except Exception:
        print(Exception)
    return results1 + results2


def set_fnames(ID, fnames, redis_server):
    """ Set list of names of all files associated with item ID and set
    filename of preview image.
    
    Args:
    ID: string containing unique item ID (uuid4)
    fnames: list with all enumerated filenames (all files uploaded)
    pname: name of file containing cropped image preview
    redis_server: instance of Strict Redis server
    """
    redis_server.hset(ID, "fnames", fnames)
    redis_server.bgsave()


def set_preview(ID, pname, pindex, pcoords, redis_server):
    redis_server.hset(ID, "pname", pname)
    redis_server.hset(ID, "pindex", pindex)
    redis_server.hset(ID, "pxcoord", pcoords[0])
    redis_server.hset(ID, "pycoord", pcoords[1])


def get_fnames(ID, redis_server):
    """ Returns list of names of all files associated with item ID.
    Example return value = ["01.jpg", "02.png"]
    
    Args:
    ID: string containing unique item ID (uuid4)
    redis_server: instance of Strict Redis server

    Returns:
    list of all filenames associated with item
    """
    return ast.literal_eval(redis_server.hget(ID, "fnames"))


def get_result_entry_data(ID, redis_server):
    data = {}
    data['thumbpath'] = url_for('static', filename=os.path.join('doc_data', ID, get_fnames(ID, redis_server)[0]))
    data['name'] = redis_server.hget(ID, 'name')
    data['school'] = redis_server.hget(ID, 'school')
    data['course'] = redis_server.hget(ID, 'course')
    return data


def get_comments(ID, redis_server, format_times=False):
    """ Returns list of names of all files associated with item ID.
    Example return value = ["01.jpg", "02.png"]
    
    Args:
    ID: string containing unique item ID (uuid4)
    redis_server: instance of Strict Redis server

    Returns:
    list of all filenames associated with item
    """
    comment_data = redis_server.hget(ID, "comments")
    if comment_data is None:
        return []
    comments = ast.literal_eval(comment_data)
    if format_times:
        for comment in comments:
            comment['time'] = formatTime(comment['time'])
    return comments


def like_comment(ID, index, username, redis_server):
    comments = get_comments(ID, redis_server)
    if comments[len(comments) - 1 - index].get('likes'):
        comments[len(comments) - 1 - index]['likes'] += 1
    else:
        comments[len(comments) - 1 - index]['likes'] = 1
    if comments[len(comments) - 1 - index].get('dusers') and username in comments[len(comments) - 1 - index]['dusers']:
        comments[len(comments) - 1 - index]['dusers'].remove(username)
        comments[len(comments) - 1 - index]['likes'] += 1
    comments[len(comments) - 1 - index].setdefault('lusers', []).append(username)
    redis_server.hset(ID, "comments", comments)


def dislike_comment(ID, index, username, redis_server):
    comments = get_comments(ID, redis_server)
    if comments[len(comments) - 1 - index].get('likes'):
        comments[len(comments) - 1 - index]['likes'] -= 1
    else:
        comments[len(comments) - 1 - index]['likes'] = -1
    if comments[len(comments) - 1 - index].get('lusers') and username in comments[len(comments) - 1 - index]['lusers']:
        comments[len(comments) - 1 - index]['lusers'].remove(username)
        comments[len(comments) - 1 - index]['likes'] -= 1
    comments[len(comments) - 1 - index].setdefault('dusers', []).append(username)
    redis_server.hset(ID, "comments", comments)


def nullify_comment(ID, index, username, redis_server):
    comments = get_comments(ID, redis_server)
    if comments[len(comments) - 1 - index].get('lusers') and username in comments[len(comments) - 1 - index]['lusers']:
        comments[len(comments) - 1 - index]['lusers'].remove(username)
        comments[len(comments) - 1 - index]['likes'] -= 1
    elif comments[len(comments) - 1 - index].get('dusers') and username in comments[len(comments) - 1 - index][
        'dusers']:
        comments[len(comments) - 1 - index]['dusers'].remove(username)
        comments[len(comments) - 1 - index]['likes'] += 1
    redis_server.hset(ID, "comments", comments)


def add_comment_reply(ID, index, comment, user, redis_server):
    comments = get_comments(ID, redis_server)
    comments[len(comments) - 1 - index].setdefault('replies', []).insert(0, {'text': comment, 'user': user,
                                                                             'time': get_time()})
    redis_server.hset(ID, "comments", comments)


def add_comment(ID, comment, user, redis_server):
    comments = get_comments(ID, redis_server)
    index = int(redis_server.hget(ID, 'nextCommentIndex') or 0)
    comments.insert(0, {'text': comment, 'user': user, 'time': get_time(), 'i': index})
    redis_server.hset(ID, "nextCommentIndex", index + 1)
    redis_server.hset(ID, "comments", comments)


def get_preview(ID, redis_server):
    return redis_server.hget(ID, "pname")


def edit_entry(ID, key, value, redis_server):
    """ Edit an existing hash entry in Redis..

    Args:
        ID: string containing ID of assignment uploaded
        key: string containing key of data field that will be modified
        value: string containing data to assign to that data field
        redis_server: instance of Strict Redis server
    """
    redis_server.hset(ID, key, value)
    redis_server.bgsave()


def delete_entry(ID, redis_server):
    """ Remove entry from database.

    Args:
        ID: string representation of entry ID.
        redis_server: instance of Strict Redis server
    """
    redis_server.srem("entries", ID)
    redis_server.delete(ID)


def get_entry(ID, redis_server):
    """ Retrieves Redis hash from database to return.

    Args:
        ID: string representation of ID of assignment to retrieve
        redis_server: instance of Strict Redis server

    Returns:
        hash representation of assignment information.
    """
    data = {}
    data['school'] = redis_server.hget(ID, 'school')
    data['course'] = redis_server.hget(ID, 'course')
    data['kind'] = redis_server.hget(ID, 'kind')
    data['name'] = redis_server.hget(ID, 'name')
    data['time'] = redis_server.hget(ID, 'time')
    data['user'] = redis_server.hget(ID, 'user')
    data['comments'] = get_comments(ID, redis_server)
    return data


def process_img_data(ID, redis_server):
    pname = redis_server.hget(ID, "pname")
    pindex = int(redis_server.hget(ID, "pindex"))
    fnames = get_fnames(ID, redis_server)
    preview_path = os.path.join('static', 'doc_data', ID, pname)
    coords = (int(redis_server.hget(ID, 'pxcoord')), int(redis_server.hget(ID, 'pycoord')))
    preview = Image.open(preview_path)

    paths = []
    for i, fname in enumerate(fnames):
        print(fname)
        ext = re.findall('\.\w+$', fname)[0]
        image_path = os.path.join('static', 'doc_data', ID, fname)
        image = Image.open(image_path)
        blurred_image = image.filter(ImageFilter.BLUR)
        if i == pindex:
            blurred_image.paste(preview, coords)
        blurred_image.save(os.path.join('static', 'doc_data', ID, "{0:0>2}".format(i) + "_blur" + ext))
        paths += [os.path.join('static', 'doc_data', ID, "{0:0>2}".format(i) + "_blur" + ext)]
    return paths


def get_time():
    return json.dumps(datetime.now(), default=lambda obj: (
        obj.isoformat()
        if isinstance(obj, (datetime, datetime.date))
        else None
    )).strip("\"")


def too_many_requests(redis_server, allowed=100, minutes=1):
    return redis_server.llen('ipreq') == allowed and datetime.now() - datetime.strptime(
        redis_server.lrange('ipreq', -1, -1)[0], '%y%m%d%H%M%S') < timedelta(minutes=minutes)


def formatTime(time):
    now = get_time()
    diff = 0
    unit = ""
    for i in range(0, len(time), 2):
        if int(time[i: i + 2]) < int(now[i: i + 2]):
            unit = timeunits[i // 2]
            diff = abs(int(time[i: i + 2]) - int(now[i: i + 2]))
            if diff != 1:
                return " {} {}s ago".format(diff, unit)
            else:
                return " {} {} ago".format(diff, unit)
    return " just now"


def get_school(sid):
    for college, info in college_data.items():
        if info['sid'] == sid:
            return college
