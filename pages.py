from flask import Flask, url_for, request, render_template, redirect, abort, current_app, session, send_from_directory
from flask_login import logout_user, current_user, login_required, LoginManager
from GradeTip.models import redis_server
from GradeTip.models.users import User, create_user
from GradeTip.models.entries import (create_entry, edit_entry, delete_entry,
                                   set_fnames, get_fnames, set_preview,
                                   get_preview, process_img_data, get_entry,
                                   get_comments, add_comment, dislike_comment,
                                   like_comment, nullify_comment,
                                   get_matching_entries)
from GradeTip.models.session import (validate_login, create_session,
                                   get_session, delete_session)
from GradeTip.config.errors import errors
from werkzeug import secure_filename, FileStorage
from PIL import Image, ImageFilter
import bcrypt
import re
import os
import json
from uuid import uuid4
import ast
import datetime


app = Flask(__name__, static_folder='static')
app.config.update(DEBUG=False, SECRET_KEY=os.urandom(24),
                  SESSION_COOKIE_SECURE=True)
with open('course_catalog.json', 'r') as f:
    data = json.load(f)

login_manager = LoginManager()
login_manager.login_view = 'loginpage'
login_manager.session_protection = 'strong'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(username):
    """ Called every time a request is made by the user. Load User session for
    each request.

    Args:
        username: string represenation of User's username.
    """

    return User.get(username, redis_server)

@app.route('/login', methods=['GET', 'POST'])
def loginpage():
    """ Displays login page if not logged in and redirects to index page or
    next page in request if already authenticated.

    If user submits login request, check validation of username and password.
    For valid login, create a user session and redirect to index or next page
    in request. For invalid login, display login page with error.

    If user is logged out in the middle of session, login should redirect to
    page in prior session.

    Returns:
        Rendered page template from the templates folder.
    """

    # If next page has not been defined yet, default to None

    error = None
    if request.method == 'POST':
        # Obtain username and password from login request
        email = request.form['username']
        password = request.form['password']

        # Create session in Redis if login is valid. Otherwise display error.
        if validate_login(email, password, redis_server):
            create_session(email, redis_server)
            return redirect(url_for('index'))
        else:
            error = True
    else:
        # Record next page to redirect to (if available)
        loginpage.next = request.values.get('next')

        # Already logged users can go to index page
        if current_user.is_authenticated:
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def registerpage():
    """ Page for new users to create an account.
    """
    if request.method == 'POST':
        school = request.form['element_1']
        email = request.form['element_2']
        password = request.form['element_3']
        displayName = request.form['element_5']
        passwordHash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        create_user(redis_server, email, passwordHash, school, displayName)
    return render_template('register.html', colleges=list(data.keys()), animals=animals, adjectives=adjectives)


@app.route('/study', methods=['GET', 'POST'])
def studypage():
    # TODO
    return render_template('sell.html')

@app.route('/sell', methods=['GET', 'POST'])
def sellpage():
    """ On POST, retrieves sell form info from template and generates unique uuid4 for new
    item listing. Entry is then created in redis with info about item. User is redirected to
    upload page with ID as URL parameter
    (Example: GradeTip.com/upload?ID=467c15cc-bd1f-4f59-a5c7-afc1ef39d886)

    On GET, loads sell form to user.
    """
    if request.method == 'POST':
        school = request.form['element_1'].strip(' \t\n\r')
        course = request.form['element_2'].strip(' \t\n\r')
        name = request.form['element_3'].strip(' \t\n\r')
        kind = request.form['element_4'].strip(' \t\n\r')
        ID = uuid4()
        while redis_server.exists(ID):
            ID = uuid4()
        create_entry(school, course, kind, name, ID, redis_server)
        return redirect(url_for('uploadpage', ID=ID))
    return render_template('sell.html', colleges=list(data.keys()), data=data)

@app.route('/upload', methods=['GET', 'POST'])
def uploadpage():
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

@app.route('/addcomment', methods=['POST'])
def addcomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    comment = request.form['comment']
    add_comment(ID, comment, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))

@app.route('/likecomment', methods=['POST'])
def likecomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    like_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))

@app.route('/dislikecomment', methods=['POST'])
def dislikecomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    dislike_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))

@app.route('/nullifycomment', methods=['POST'])
def nullifycomment():
    ID = re.findall(r'.*\?ID=([a-zA-Z0-9-]*)', request.referrer)[0]
    index = int(request.form['index'])
    nullify_comment(ID, index, "AnonymousUser", redis_server)
    return json.dumps(get_comments(ID, redis_server, format_times=True))

@app.route('/', methods=['GET', 'POST'])
def index():
    """ Main page of GradeTip with search bar for finding assignment entries.
    
    Returns:
        Rendered page template from the templates folder.
    """
    if request.method == 'POST':
        query = request.form.get('squery')
        return redirect(url_for('resultspage',q=query))
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def resultspage():
    query = request.args.get('q')
    if not query:
        abort(404)
    results = get_matching_entries(query, redis_server)
    print(results)
    return render_template('search.html', results=results)

@app.route('/item',  methods=['GET', 'POST'])
def itempage():
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

@app.route('/logout')
def logout():
    """ Defines logout route behavior and backend. Redirects to login page if
    not logged in. Deletes user session entry from database and logs out User
    session. User will have to log back in to access pages.

    Returns:
        Rendered page template from the templates folder.
    """
    if current_user.is_authenticated:
        delete_session(redis_server)
        logout_user()
    return redirect(url_for('loginpage'))

@app.errorhandler(500)
def internal_server_error(error):
    """ Displays Internal Server Error message.

    Args:
        error: string representation of error message from application.

    Returns:
        Rendered error template from the templates folder.
    """
    return render_template('error.html', error=error), 500

@app.errorhandler(404)
def page_not_found(error):
    """ Displays Page Not Found Error message.

    Args:
        error: string representation of error message from application.

    Returns:
        Rendered error template from the templates folder.
    """
    return render_template('error.html', error=error,
                           error_message=errors["not_found"]), 404

