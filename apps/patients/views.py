"""Patient views."""

from typing import Any

from rest_framework import serializers as drf_serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOwner
from apps.patients.filters import PatientFilter
from apps.patients.models import Patient
from apps.patients.serializers import PatientDetailSerializer, PatientListSerializer


class PatientViewSet(ModelViewSet):  # type: ignore[type-arg]
    """CRUD for patients — scoped to the authenticated user."""

    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = PatientFilter

    def get_queryset(self) -> Any:
        if getattr(self, "swagger_fake_view", False):
            return Patient.objects.none()
        return Patient.objects.filter(created_by=self.request.user).select_related(  # type: ignore[misc]
            "created_by"
        )

    def get_serializer_class(self) -> type[drf_serializers.Serializer]:  # type: ignore[type-arg]
        if self.action == "list":
            return PatientListSerializer
        return PatientDetailSerializer

    def perform_create(self, serializer: drf_serializers.Serializer) -> None:  # type: ignore[type-arg,override]
        serializer.save(created_by=self.request.user)
