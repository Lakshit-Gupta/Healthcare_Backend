"""Shared model mixins."""

import uuid

from django.db import models
from uuid_utils import uuid7 as _uuid7


def uuid7() -> uuid.UUID:
    """Generate a UUID7 as a stdlib uuid.UUID (Django UUIDField compatible)."""
    return uuid.UUID(str(_uuid7()))


class TimestampMixin(models.Model):
    """Abstract mixin providing UUID7 PK and created/updated timestamps."""

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
