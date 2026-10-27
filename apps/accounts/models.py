"""Custom user model with email authentication."""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower

from apps.accounts.managers import UserManager
from apps.core.mixins import uuid7


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user — email is the primary identifier, not username."""

    id = models.UUIDField(primary_key=True, default=uuid7, editable=False)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        indexes = [
            models.Index(
                Lower("email"),
                name="idx_user_lower_email",
            ),
        ]

    def __str__(self) -> str:
        return self.email
