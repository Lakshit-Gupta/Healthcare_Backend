"""Doctor model."""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin


class Doctor(TimestampMixin):
    """Doctor record — visible to all authenticated users."""

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="doctors",
    )
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["specialization"],
                name="idx_doctor_specialization",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.specialization})"
