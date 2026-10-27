"""Development settings."""

from config.settings.base import *  # noqa: F403, F401

DEBUG = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

INSTALLED_APPS += ["debug_toolbar"]  # noqa: F405

MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")  # noqa: F405

INTERNAL_IPS = ["127.0.0.1"]

# Shorter connection lifetime in dev
DATABASES["default"]["CONN_MAX_AGE"] = 0  # noqa: F405
