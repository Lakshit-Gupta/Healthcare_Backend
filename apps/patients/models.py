"""Patient model."""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin


class Patient(TimestampMixin):
    """Patient record owned by the creating user."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="patients",
    )
    name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    medical_history = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["created_by", "-created_at"],
                name="idx_patient_owner_created",
            ),
            models.Index(
                fields=["created_by"],
                include=["name", "created_at"],
                name="idx_patient_owner_covering",
            ),
        ]

    def __str__(self) -> str:
        return self.name
