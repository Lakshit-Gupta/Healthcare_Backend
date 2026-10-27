"""Test settings — fast, isolated."""

from config.settings.base import *  # noqa: F403, F401

# Fast password hashing — saves ~90% test CPU time
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# No persistent connections in tests
DATABASES["default"]["CONN_MAX_AGE"] = 0  # noqa: F405

# Raise throttle limits so per-view AnonRateThrottle never fires during tests
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/min",
    "user": "1000/min",
}
