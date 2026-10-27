"""Doctor views."""

from typing import Any

from rest_framework import serializers as drf_serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from apps.accounts.permissions import IsOwner
from apps.doctors.filters import DoctorFilter
from apps.doctors.models import Doctor
from apps.doctors.serializers import DoctorDetailSerializer, DoctorListSerializer


class DoctorViewSet(ModelViewSet):  # type: ignore[type-arg]
    """CRUD for doctors — all doctors visible to authenticated users."""

    permission_classes = [IsAuthenticated, IsOwner]
    filterset_class = DoctorFilter

    def get_queryset(self) -> Any:
        return Doctor.objects.select_related("created_by").all()

    def get_serializer_class(self) -> type[drf_serializers.Serializer]:  # type: ignore[type-arg]
        if self.action == "list":
            return DoctorListSerializer
        return DoctorDetailSerializer

    def perform_create(self, serializer: drf_serializers.Serializer) -> None:  # type: ignore[type-arg,override]
        serializer.save(created_by=self.request.user)
