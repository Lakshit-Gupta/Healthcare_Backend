"""Account serializers — registration and JWT."""

from typing import Any

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

MIN_PASSWORD_LENGTH = 8


class RegisterSerializer(serializers.ModelSerializer):  # type: ignore[type-arg]
    """Serializer for user registration."""

    password = serializers.CharField(
        write_only=True,
        min_length=MIN_PASSWORD_LENGTH,
        style={"input_type": "password"},
    )

    class Meta:
        model = User
        fields = ["id", "email", "name", "password"]
        read_only_fields = ["id", "created_at"]

    def create(self, validated_data: dict[str, Any]) -> Any:
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Add user info to JWT response."""

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        data: dict[str, Any] = super().validate(attrs)
        user = self.user
        if user is not None:
            data["user"] = {
                "id": str(user.id),
                "email": user.email,
                "name": getattr(user, "name", ""),
            }
        return data
