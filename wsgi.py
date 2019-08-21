#!/usr/bin/env python
"""
    Start app. Run this file, with WSGI, to start GradeTip in localhost:5000.
"""

import app
application = app.create_app()


# Start GradeTip
if __name__ == '__main__':
    application.run(host='0.0.0.0')
