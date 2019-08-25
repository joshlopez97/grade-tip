from flask import Flask
from flask_login import LoginManager
from jinja2 import contextfilter
from werkzeug.exceptions import default_exceptions
from datetime import datetime
import os
import re
from types import FunctionType

from GradeTip.admin.requests import fetch_post_requests, approve_request, deny_request
from GradeTip.models.users import User
from GradeTip import ajax
from GradeTip import pages
from GradeTip.pages import (loginpage, registerpage, logout, index,
                            internal_server_error, page_not_found, school, monitor, details)
from GradeTip.models import redis_server
from GradeTip.location import nearest

""" Flask login manager. """
login_manager = LoginManager()


def create_app():
    """ Creates Flask application and calls other setup functions.

    Returns:
        app: created application
    """

    app = Flask(__name__, static_folder='static',
                static_url_path='')
    app.config.update(DEBUG=True,
                      SECRET_KEY=os.urandom(24),
                      SESSION_COOKIE_SECURE=True,
                      SEND_FILE_MAX_AGE_DEFAULT=0,
                      MAX_CONTENT_LENGTH=2 * 1024 * 1024)
    register_routes(app)
    admin_routes(app)
    register_error_handlers(app)
    setup_login_manager(app)
    app.add_template_filter(bust_cache)
    return app


def register_routes(app):
    """ Register application routes from pages with appropriate methods.

    Args:
        app: current application
    """
    app.add_url_rule('/login', 'loginpage', loginpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', index,
                     methods=['GET', 'POST'])
    app.add_url_rule('/register', 'registerpage', registerpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/school/<school_id>', 'school', school,
                     methods=['GET', 'POST'])
    app.add_url_rule('/school/<school_id>/<post_id>', 'details', details,
                     methods=['GET', 'POST'])
    app.add_url_rule('/logout', 'logout', logout)

    # All functions in ajax.py and pages.py are registered as routes
    for resource in [ajax, pages]:
        for fxn in dir(resource):
            fxn = resource.__dict__.get(fxn)
            if isinstance(fxn, FunctionType):
                name = fxn.__name__
                app.add_url_rule('/' + name, name, fxn, methods=['GET', 'POST'])

    # Geolocation routes
    app.add_url_rule('/nearest', 'nearest', nearest, methods=['POST'])


def admin_routes(app):
    app.add_url_rule('/monitor', 'monitor', monitor,
                     methods=['GET', 'POST'])
    app.add_url_rule('/admin/requests', '/admin/requests', fetch_post_requests,
                     methods=['GET'])
    app.add_url_rule('/admin/approve/<request_id>', '/admin/approve', approve_request,
                     methods=['GET'])
    app.add_url_rule('/admin/deny/<request_id>', '/admin/deny', deny_request,
                     methods=['GET'])


def register_error_handlers(app):
    """ Register 404 and 500 error handlers with application.

    Args:
        app: current application
    """
    app.errorhandler(404)(page_not_found)
    app.errorhandler(500)(internal_server_error)


def setup_login_manager(app):
    """ Setup Flask-login with application.

    Args:
        app: current application
    """

    login_manager.login_view = 'loginpage'
    login_manager.session_protection = 'strong'
    login_manager.init_app(app)


def bust_cache(url, sid=None):
    # TODO: Configure cache busting for dev environment only
    # if sid:
    #     return re.sub(r'(\.[^\.]+)$', r'.' + sid + r'\1', url)
    # return re.sub(r'(\.[^\.]+)$', r'.' + datetime.now().strftime("%m%d%y%H%M%S") + r'\1', url)
    return url


@login_manager.user_loader
def load_user(username):
    """ Called every time a request is made by the user. Load User session for
    each request.

    Args:
        username: string represenation of User's username.
    """

    return User.get(username, redis_server)

