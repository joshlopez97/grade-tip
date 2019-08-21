from flask import Flask, url_for, request, render_template, redirect, abort, session, send_from_directory
from flask_login import logout_user, current_user, login_required
from GradeTip.models import redis_server
from GradeTip.models.entries import (create_entry, edit_entry, delete_entry,
                                     set_fnames, get_fnames, set_preview,
                                     get_preview, process_img_data, get_entry,
                                     get_comments, add_comment, dislike_comment,
                                     like_comment, nullify_comment,
                                     get_matching_entries)
from GradeTip.models.session import (validate_login, create_session,
                                     get_session, delete_session)
from GradeTip.config.errors import errors
from PIL import Image
import bcrypt
import re
import os
import json
import random
from uuid import uuid4

def account():
    return render_template('account.html')

def sell():
    """ On POST, retrieves sell form info from template and generates unique uuid4 for new
    item listing. Entry is then created in redis with info about item. User is redirected to
    upload page with ID as URL parameter
    (Example: GradeTip.com/upload?ID=467c15cc-bd1f-4f59-a5c7-afc1ef39d886)

    On GET, loads sell form to user.
    """
    if request.method == 'POST':
        school = request.form['school'].strip(' \t\n\r')
        course = request.form['cid'].strip(' \t\n\r')
        name = request.form['title'].strip(' \t\n\r')
        kind = request.form['kind'].strip(' \t\n\r')

        ID = create_entry(school, course, kind, name, redis_server)
        print(ID)
        return redirect(url_for('upload', ID=ID))
    return render_template('sell.html')

def upload():
    ID = request.args.get('ID')
    if not ID:
        abort(404)
    if request.method == 'POST':
        coords = (int(request.form['x1']), int(request.form['y1']), int(request.form['x2']), int(request.form['y2']))
        files = request.files.getlist('file')
        preview_index = int(request.form['preview_index'])
        if not os.path.exists(os.path.join('static', 'doc_data', str(ID))):
            fnames = []
            os.makedirs(os.path.join('static', 'doc_data', str(ID)))
            for i, file in enumerate(files):
                ext = re.findall('\.\w+$', file.filename)[0]
                fnames += ["{0:0>2}".format(i) + ext]
                file.save(os.path.join('static', 'doc_data', str(ID), "{0:0>2}".format(i) + ext))
            ext = re.findall('\.\w+$', files[preview_index].filename)[0]
            preview = Image.open(os.path.join('static', 'doc_data', str(ID), "{0:0>2}".format(preview_index) + ext)).crop(coords)
            pname = "preview{}".format(ext)
            preview.save(os.path.join('static', 'doc_data', str(ID), pname))
            set_fnames(ID, fnames, redis_server)
            set_preview(ID, pname, preview_index, (coords[0], coords[1]), redis_server)
        return redirect(url_for('index'))
    return render_template('upload.html')


def game():
    return render_template('index2.html')

def search():
    query = request.args.get('q')
    if not query:
        abort(404)
    results = get_matching_entries(query, redis_server)
    return render_template('search.html', query=query,results=results)

def item():
    ID = request.args.get('ID')
    if not ID:
        abort(404)
    paths = process_img_data(ID, redis_server)
    data = get_entry(ID, redis_server)
    if request.method == 'POST':
        comment = request.form['comment']
        add_comment(ID, comment, "AnonymousUser", redis_server)
    comments = get_comments(ID, redis_server, format_times=True)
    return render_template('item.html', paths=paths, data=data, comments=comments, ID=ID, username="AnonymousUser")
