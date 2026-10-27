"""Account views — registration and JWT login."""

from rest_framework import generics, permissions
from rest_framework.throttling import AnonRateThrottle, BaseThrottle
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.accounts.serializers import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
)


class RegisterView(generics.CreateAPIView):  # type: ignore[type-arg]
    """Register a new user. Public endpoint."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def get_throttles(self) -> list[BaseThrottle]:
        return [AnonRateThrottle()]


class LoginView(TokenObtainPairView):
    """JWT login. Returns access + refresh tokens."""

    serializer_class = CustomTokenObtainPairSerializer

    def get_throttles(self) -> list[BaseThrottle]:
        return [AnonRateThrottle()]
