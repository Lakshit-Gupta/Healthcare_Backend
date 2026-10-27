"""Patient serializers — list (light) and detail (full)."""

from rest_framework import serializers

from apps.patients.models import Patient


class PatientListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Light serializer for list views — excludes heavy fields."""

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "date_of_birth",
            "phone",
            "email",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class PatientDetailSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Full serializer for detail/create/update views."""

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "date_of_birth",
            "phone",
            "email",
            "address",
            "medical_history",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
