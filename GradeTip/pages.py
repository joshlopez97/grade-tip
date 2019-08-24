import bcrypt
import os
import re

from PIL import Image
from flask import url_for, request, render_template, redirect, abort, jsonify, current_app as app
from flask_login import current_user, logout_user

from GradeTip.admin.auth import is_admin
from GradeTip.content.posts import validate_post_data, create_post, request_post
from GradeTip.models import redis_server
from GradeTip.models.entries import (create_entry, set_fnames, set_preview,
                                     process_img_data, get_entry,
                                     get_comments, add_comment, get_matching_entries, get_school)
from GradeTip.models.session import delete_session, create_session, validate_login
from GradeTip.models.users import create_user


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
            preview = Image.open(
                os.path.join('static', 'doc_data', str(ID), "{0:0>2}".format(preview_index) + ext)).crop(coords)
            pname = "preview{}".format(ext)
            preview.save(os.path.join('static', 'doc_data', str(ID), pname))
            set_fnames(ID, fnames, redis_server)
            set_preview(ID, pname, preview_index, (coords[0], coords[1]), redis_server)
        return redirect(url_for('index'))
    return render_template('upload.html')


def search():
    query = request.args.get('q')
    if not query:
        abort(404)
    results = get_matching_entries(query, redis_server)
    return render_template('search.html', query=query, results=results)


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


def monitor():
    if current_user.is_authenticated and is_admin(current_user):
        return render_template('monitor.html')
    return abort(404)


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
    try:
        loginpage.next
    except AttributeError:
        loginpage.next = None

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
            return redirect_next(loginpage.next)
    return render_template('login.html', error=error)


def redirect_next(next_page):
    """ Utility function to redirect to index if next_page is None, otherwise
    redirect to next_page.

    Args:
        next_page: path to next page that user was trying to visit before
            loginpage or None if user went directly to loginpage

    Returns:
        redirect to index or next_page
    """

    # Reset loginpage.next for next session
    loginpage.next = None
    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('index'))


def index():
    """ Main page of GradeTip with search bar for finding assignment entries.

    Returns:
        Rendered page template from the templates folder.
    """

    if request.method == 'POST':
        query = request.form.get('squery')
        return redirect(url_for('resultspage', q=query))
    return render_template('index.html')


def registerpage():
    """ Page for new users to create an account. Nouns.txt and adjectives_names.txt contain
    random words for generating usernames. They are passed as parameters to Jinja template.
    In a post request, all required input fields are taken and a new user is created.
    """
    if request.method == 'POST':
        school_name = request.form['element_1']
        email = request.form['element_2']
        password = request.form['element_3']
        displayName = request.form['element_5']
        passwordHash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        create_user(redis_server, email, passwordHash, school_name, displayName)
        create_session(email, redis_server)
        return redirect(url_for('index'))

    return render_template('register.html')


def school(school_id):
    school_name = get_school(int(school_id))
    if not school_name:
        abort(404)

    # user submitted request for post to be created
    if request.method == 'POST' and validate_post_data(request.form):
        # log & return json indicating if request was successfully submitted
        if not request_post(redis_server, school_id, request.form):
            app.logger.info("Could not create request with {}".format(str(request.form)))
            return jsonify({"requested": False, "created": False})
        app.logger.info("Created request for post " + str(request.form))
        return jsonify({"requested": True, "created": False})

    return render_template('school.html', school=school_name, sid=school_id)


def details(school_id, post_id):
    school_name = get_school(int(school_id))
    if not school_name:
        abort(404)
    return render_template('school.html', school=school_name, sid=school_id, pid=post_id)


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


def internal_server_error(error):
    """ Displays Internal Server Error message.

    Args:
        error: string representation of error message from application.

    Returns:
        Rendered error template from the templates folder.
    """
    return render_template('error.html',
                           error="Our servers seem to be down. Please wait while we fix this problem!"), 500


def page_not_found(error):
    """ Displays Page Not Found Error message.

    Args:
        error: string representation of error message from application.

    Returns:
        Rendered error template from the templates folder.
    """
    return render_template('error.html', error="Sorry, that page doesn't exist!",
                           error_message="If you entered the URL manually please check your spelling and try again."), 404
