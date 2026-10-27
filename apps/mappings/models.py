"""Patient-Doctor mapping model."""

from django.conf import settings
from django.db import models

from apps.core.mixins import TimestampMixin


class PatientDoctorMapping(TimestampMixin):
    """Explicit M2M between Patient and Doctor with audit trail."""

    patient = models.ForeignKey(
        "patients.Patient",
        on_delete=models.CASCADE,
        related_name="doctor_mappings",
    )
    doctor = models.ForeignKey(
        "doctors.Doctor",
        on_delete=models.CASCADE,
        related_name="patient_mappings",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mappings",
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["patient", "doctor"],
                name="uniq_patient_doctor",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.patient.name} ↔ {self.doctor.name}"
