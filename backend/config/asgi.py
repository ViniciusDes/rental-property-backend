"""
ASGI config for rental project.

ASGI (Asynchronous Server Gateway Interface) is similar to Node.js async/await patterns.
For WebSockets and async operations, similar to Socket.io in Node.js.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.config.settings')

application = get_asgi_application()
