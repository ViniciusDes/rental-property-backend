"""
WSGI config for rental project.

WSGI (Web Server Gateway Interface) is similar to how Node.js HTTP server works.
In production, you'd use Gunicorn (similar to PM2 in Node.js) to run this.

In Node.js: const server = http.createServer(app);
In Django: WSGI application serves the same purpose
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

application = get_wsgi_application()
