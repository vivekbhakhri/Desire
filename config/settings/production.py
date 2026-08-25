"""Production settings: secret enforcement + security headers + HTTPS.

Activate with:

    DJANGO_SETTINGS_MODULE=config.settings.production

The Azure-specific overrides (Postgres + Azure blob storage) live in
`config/settings/azure.py` and extend this module.
"""
from decouple import config

from .base import *  # noqa: F401,F403

DEBUG = False

# Fail fast in production if SECRET_KEY wasn't supplied.
SECRET_KEY = config("SECRET_KEY", default="")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in production")––

# HTTPS / cookie hardening.
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
