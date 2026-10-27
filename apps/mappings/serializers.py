"""Mapping serializers — create + list."""

from typing import Any

from rest_framework import serializers

from apps.mappings.models import PatientDoctorMapping


class MappingSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for creating and listing patient-doctor mappings."""

    class Meta:
        model = PatientDoctorMapping
        fields = [
            "id",
            "patient",
            "doctor",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]
        # Disable DRF's auto UniqueTogetherValidator — we rely on the DB
        # constraint + select_for_update to return 409 on duplicates.
        validators: list[object] = []

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Ensure the requesting user owns the patient."""
        request = self.context.get("request")
        patient = attrs.get("patient")
        if request and patient and patient.created_by != request.user:
            raise serializers.ValidationError(
                {"patient": "You can only assign doctors to your own patients."}
            )
        return attrs
