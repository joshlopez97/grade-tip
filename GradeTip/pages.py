import os
import re

import bcrypt
from PIL import Image
from flask import url_for, request, render_template, redirect, abort, jsonify, current_app as app
from flask_login import current_user, logout_user

from GradeTip.admin import admin_authenticator
from GradeTip.content import listing_manager, request_manager
from GradeTip.models import redis_server
from GradeTip.models.entries import (set_fnames, set_preview,
                                     get_matching_entries, get_school)
from GradeTip.models.sessions import delete_session, create_session, validate_login
from GradeTip.models.users import create_user


def account():
    return render_template('account.html')


def sell():
    """ On POST, retrieves sell form info and file upload and creates a request
    to be approved by moderators.

    On GET, loads sell form to user.
    """
    school_id = request.args.get("sid")
    if request.method == 'POST':
        file = request.files.get('file')
        listing_manager.request_listing(request.form, file)

    return render_template('sell.html', sid=school_id)


def monitor():
    if admin_authenticator.is_admin(current_user):
        email = current_user.id
        sessionID = current_user.session_id
        return render_template('monitor.html', email=email, sessionID=sessionID)
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

    return render_template('index.html')


def registerpage():
    """ Page for new users to create an account. Nouns.txt and adjectives_names.txt contain
    random words for generating usernames. They are passed as parameters to Jinja template.
    In a post request, all required input fields are taken and a new user is created.
    """
    if request.method == 'POST':
        school_name = request.form['school']
        email = request.form['email']
        password = request.form['password']
        displayName = request.form['displayname']
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
    if request.method == 'POST':
        # log & return json indicating if request was successfully submitted
        if not request_manager.request_post(redis_server, school_id, request.form):
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
