"""Azure App Service overrides: Postgres database + Azure blob storage."""
import os

from .production import *  # noqa: F401,F403

ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["APP_DB_NAME"],
        "USER": "{}@{}".format(
            os.environ["POSTGRES_ADMIN_USER"], os.environ["POSTGRES_SERVER_NAME"]
        ),
        "PASSWORD": os.environ["POSTGRES_ADMIN_PASSWORD"],
        "HOST": os.environ["POSTGRES_HOST"],
        "PORT": "5432",
        "OPTIONS": {"sslmode": "require"},
    }
}

STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "storages.backends.azure_storage.AzureStorage"},
}
AZURE_ACCOUNT_NAME = os.environ["AZ_STORAGE_ACCOUNT_NAME"]
AZURE_CONTAINER = os.environ["AZ_STORAGE_CONTAINER"]
AZURE_ACCOUNT_KEY = os.environ["AZ_STORAGE_KEY"]
