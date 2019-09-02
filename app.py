import os

from flask import Flask
from flask_login import LoginManager

from GradeTip.content.resources import posts_by_sid, fetch_post_requests, approve_request, deny_request
from GradeTip.pages import (loginpage, registerpage, logout, indexpage,
                            internal_server_error, page_not_found, schoolpage, monitorpage, detailspage, sellpage,
                            aboutpage, termspage, privacypage)
from GradeTip.schools.resources import nearest, colleges
from GradeTip.user import user_manager
from GradeTip.user.resources import usernames, validate_email

""" Flask login manager. """
login_manager = LoginManager()


def create_app():
    """ Creates Flask application and calls other setup functions.

    Returns:
        app: created application
    """

    app = Flask(__name__, static_folder='static', static_url_path='')
    app.config.from_pyfile("config/settings.cfg")
    app.config.update(SECRET_KEY=os.urandom(24))
    register_page_routes(app)
    register_api_routes(app)
    register_error_handlers(app)
    setup_login_manager(app)
    app.add_template_filter(bust_cache)
    return app


def register_page_routes(app):
    """ Register application routes from pages with appropriate methods.

    Args:
        app: current application
    """
    app.add_url_rule('/login', 'loginpage', loginpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/', 'index', indexpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/register', 'registerpage', registerpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/upload', 'uploadpage', sellpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/school/<school_id>', 'school', schoolpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/school/<school_id>/<post_id>', 'details', detailspage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/monitor', 'monitor', monitorpage,
                     methods=['GET', 'POST'])
    app.add_url_rule('/about', 'about', aboutpage,
                     methods=['GET'])
    app.add_url_rule('/terms', 'terms', termspage,
                     methods=['GET'])
    app.add_url_rule('/privacy', 'privacy', privacypage,
                     methods=['GET'])
    app.add_url_rule('/logout', 'logout', logout)


def register_api_routes(app):
    # Content-related endpoints
    app.add_url_rule('/admin/requests', '/admin/requests', fetch_post_requests,
                     methods=['GET'])
    app.add_url_rule('/admin/approve/<request_id>', '/admin/approve', approve_request,
                     methods=['GET'])
    app.add_url_rule('/admin/deny/<request_id>', '/admin/deny', deny_request,
                     methods=['GET'])
    app.add_url_rule('/school/posts', '/school/posts', posts_by_sid,
                     methods=['POST'])

    # School-related endpoints
    app.add_url_rule('/nearest', 'nearest', nearest,
                     methods=['POST'])
    app.add_url_rule('/colleges', 'colleges', colleges,
                     methods=['GET'])

    # User-related endpoints
    app.add_url_rule('/usernames', 'usernames', usernames,
                     methods=['GET'])
    app.add_url_rule('/validate_email', 'validate_email', validate_email,
                     methods=['POST'])


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
def load_user(email):
    """
    Return User object matching user with provided email address
    :param email: user email
    :return: User object containing user data
    """

    return user_manager.create_user(email)

