"""Local development settings.

Defaults are deliberately permissive — DEBUG on, console email backend, no
HTTPS enforcement. Activate with:

    DJANGO_SETTINGS_MODULE=config.settings.development
"""
from .base import *  # noqa: F401,F403

DEBUG = True

# In dev we don't want to send real emails by accident.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Verbose application logging while developing.
LOGGING["loggers"]["shop"]["level"] = "DEBUG"  # noqa: F405
