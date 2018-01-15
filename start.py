#!/usr/bin/env python
"""
    Start app. Run this file, with WSGI, to start GradeTip in localhost:5000.
"""

from pages import app

# Start GradeTip
if __name__ == '__main__':
    app.run()
