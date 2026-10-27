"""Doctor serializers — list (light) and detail (full)."""

from rest_framework import serializers

from apps.doctors.models import Doctor


class DoctorListSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Light serializer for list views."""

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialization",
            "phone",
            "email",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["id", "created_by", "created_at"]


class DoctorDetailSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Full serializer for detail/create/update views."""

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialization",
            "phone",
            "email",
            "address",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]
