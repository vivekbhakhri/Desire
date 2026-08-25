import os

from django.core.wsgi import get_wsgi_application

# Production deployments override this via the process environment.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
