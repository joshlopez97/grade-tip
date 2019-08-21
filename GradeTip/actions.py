from flask import Flask, url_for, request, render_template, redirect, abort, session, send_from_directory
from flask_login import logout_user, current_user, login_required, LoginManager
from GradeTip.models import redis_server
from GradeTip.models.users import User, create_user
from GradeTip.models.entries import (create_entry, edit_entry, delete_entry,
                                     set_fnames, get_fnames, set_preview,
                                     get_preview, process_img_data, get_entry,
                                     get_comments, add_comment, dislike_comment,
                                     like_comment, nullify_comment,
                                     get_matching_entries, get_school)
from GradeTip.models.session import (validate_login, create_session,
                                     get_session, delete_session)
from GradeTip.models.posts import (new)
from GradeTip.config.errors import errors
from PIL import Image
import bcrypt
import re
import os
import json
import random
from uuid import uuid4

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
        return redirect(url_for('resultspage',q=query))
    return render_template('index.html')

def registerpage():
    """ Page for new users to create an account. Nouns.txt and adjectives_names.txt contain
    random words for generating usernames. They are passed as parameters to Jinja template.
    In a post request, all required input fields are taken and a new user is created.
    """
    with open("static/txt/nouns.txt", "r") as f:
        animals = [line.strip('\n') for line in f]
    with open("static/txt/adjectives_names.txt", "r") as f:
        adjectives = [line.strip('\n') for line in f]
    if request.method == 'POST':
        school = request.form['element_1']
        email = request.form['element_2']
        password = request.form['element_3']
        displayName = request.form['element_5']
        passwordHash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        create_user(redis_server, email, passwordHash, school, displayName)
        create_session(email, redis_server)
        return redirect(url_for('index'))

    return render_template('register.html')

def school(sid):
    school = get_school(int(sid))
    if not school:
        abort(404)
    if request.method == 'POST':
        title = request.form.get("Title","")
        body = request.form.get("Body","")
        course = request.form.get("Course","")
        
        new(redis_server,sid,title,body,course)

    return render_template('school.html',school=school,sid=sid)



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
    return render_template('error.html', error="Our servers seem to be down. Please wait while we fix this problem!"), 500

def page_not_found(error):
    """ Displays Page Not Found Error message.

    Args:
        error: string representation of error message from application.

    Returns:
        Rendered error template from the templates folder.
    """
    return render_template('error.html', error="Sorry, that page doesn't exist!",
                           error_message="If you entered the URL manually please check your spelling and try again."), 404

    