import re

import bcrypt
from flask import url_for, request, render_template, redirect, abort, jsonify, current_app as app
from flask_login import current_user, logout_user

from GradeTip.admin import admin_authenticator
from GradeTip.content import listing_store, post_store, request_store
from GradeTip.schools import schools
from GradeTip.user import session_manager, user_manager


def monitorpage():
    """
    Admin-only page for viewing post and listing requests submitted. On this page, admins
    can approve or deny these requests.
    """
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
        if session_manager.validate_login(email, password):
            session_manager.create_session(email)
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


def termspage():
    return render_template('terms.html')


def privacypage():
    return render_template('privacy.html')


def redirect_next(next_page):
    """
    Utility function to redirect to index if next_page is None, otherwise
    redirect to next_page.
    :param next_page: URL of next page to redirect to (or None)
    :return: redirect to next page
    """

    # Reset loginpage.next for next session
    loginpage.next = None
    if next_page:
        return redirect(next_page)
    else:
        return redirect(url_for('index'))


def indexpage():
    """
    Homepage of GradeTip with search bar for finding schools.
    """

    return render_template('index.html')


def aboutpage():
    """
    Simple page explaining what gradetip is and how it works.
    """
    return render_template('about.html')


def registerpage():
    """
    Page for new users to create an account.
    """
    if request.method == 'POST':
        school_name = request.form['school']
        email = request.form['email']
        password = request.form['password']
        displayName = request.form['displayname']
        passwordHash = bcrypt.hashpw(str.encode(password), bcrypt.gensalt())
        user_manager.store_user_in_redis(email, passwordHash, school_name, displayName)
        session_manager.create_session(email)
        return redirect(url_for('index'))

    return render_template('register.html')


def schoolpage(school_id):
    """
    School page for displaying all posts/content published to that school's page.
    :param school_id: the school_id for the school's page to be shown
    """
    school_name = schools.get_school_name(int(school_id))
    if not school_name:
        abort(404)
    requested_listing = request.args.get("requested")
    if requested_listing is None:
        requested_listing = "0"
    created_listing = request.args.get("created")
    if created_listing is None:
        created_listing = "0"

    # user submitted request for post to be created
    if request.method == 'POST':
        # make request
        request_id = post_store.request_post(school_id, request.form)

        # return error if request failed
        if not request_id:
            app.logger.error("Could not create request with {}".format(str(request.form)))
            return jsonify({"requested": False, "created": False})
        requested = True
        created = False

        # skip approval if config set to false
        if app.config.get("REQUIRE_POST_APPROVAL") is not None and not app.config.get("REQUIRE_POST_APPROVAL"):
            app.logger.info("Promoting request {} to post".format(request_id))
            request_store.approve_request(request_id)
            created = True

        app.logger.info("Created request for post " + str(request.form))
        return jsonify({"requested": requested, "created": created})

    return render_template('school.html',
                           school=school_name,
                           sid=school_id,
                           requested=requested_listing,
                           created=created_listing)


def listingpage():
    """ On POST, retrieves listing form info and file upload and creates a request
    to be approved by moderators.

    On GET, loads listing form to user.
    """
    school_name = ""
    school_id = request.args.get("sid")
    error = None
    if school_id is not None and re.match(r'\d+', school_id):
        school_name = schools.get_school_name(int(school_id))
    if request.method == 'POST':
        file = request.files.get('file')
        request_id = listing_store.request_listing(request.form, file)
        if not request_id:
            app.logger.error("Could not create request with {}".format(str(request.form)))
            error = "We are experiencing issues right now. Please try again later"
        else:
            # skip approval if config set to false
            if app.config.get("REQUIRE_POST_APPROVAL") is not None and not app.config.get("REQUIRE_POST_APPROVAL"):
                app.logger.info("Promoting request {} to post".format(request_id))
                request_store.approve_request(request_id)
                return redirect("/school/{}?created=1".format(schools.get_school_id(request.form.get("school"))))
            return redirect("/school/{}?requested=1".format(schools.get_school_id(request.form.get("school"))))

    return render_template('sell.html', sid=school_id, school_name=school_name, error=error)


def detailspage(school_id, post_id):
    """
    Displays a specific post on a school's page. The styling/content of this page will vary based
    on the postType.
    :param school_id: ID of school that this post was made to
    :param post_id: ID of post being viewed
    """
    school_name = schools.get_school_name(int(school_id))
    if not school_name:
        abort(404)
    return render_template('school.html', school=school_name, sid=school_id, pid=post_id)


def logout():
    """ Defines logout route behavior and backend. Redirects to login page if
    not logged in. Deletes user session entry from database and logs out User
    session. User will have to log back in to access pages.
    """
    if current_user.is_authenticated:
        session_manager.delete_session(current_user.id)
        logout_user()
    return redirect(url_for('loginpage'))


def internal_server_error(error):
    """
    Displays Internal Server Error message.
    """
    return render_template('error.html',
                           error="Our servers seem to be down. Please wait while we fix this problem!"), 500


def page_not_found(error):
    """
    Displays Page Not Found Error message.
    """
    return render_template('error.html', error="Sorry, that page doesn't exist!",
                           error_message="If you entered the URL manually please check your spelling and try again."), 404
