"""Mapping views — Create, List, Destroy (no update per spec)."""

from typing import Any

from django.db import IntegrityError, transaction
from rest_framework import mixins, status
from rest_framework import serializers as drf_serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from apps.mappings.models import PatientDoctorMapping
from apps.mappings.serializers import MappingSerializer
from apps.patients.models import Patient


class MappingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,  # type: ignore[type-arg]
):
    """Patient-Doctor mapping: create, list, list-by-patient, delete.

    GET  /api/mappings/              — list all mappings for current user
    POST /api/mappings/              — create mapping
    GET  /api/mappings/<patient_id>/ — list doctors for a specific patient
    DELETE /api/mappings/<pk>/       — delete a mapping by its own PK

    The detail route (GET /{id}/) is overridden to interpret the id as a
    patient_id and return all mappings for that patient (per SPECS.txt).
    DELETE /{id}/ still destroys the mapping whose PK matches.
    """

    serializer_class = MappingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self) -> Any:
        if getattr(self, "swagger_fake_view", False):
            return PatientDoctorMapping.objects.none()
        qs = PatientDoctorMapping.objects.select_related("patient", "doctor").filter(
            created_by=self.request.user  # type: ignore[misc]
        )
        # Support filtering by patient_id via query param
        patient_id = self.request.query_params.get("patient_id")
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        return qs

    def get_object(self) -> Any:
        """Support both 'pk' (router) and 'patient_id' (manual url) kwargs."""
        lookup = self.kwargs.get("pk") or self.kwargs.get("patient_id")
        obj = self.get_queryset().get(pk=lookup)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_create(self, serializer: drf_serializers.Serializer) -> None:  # type: ignore[type-arg,override]
        """Atomic create with select_for_update to prevent race conditions."""
        patient = serializer.validated_data["patient"]
        with transaction.atomic():
            Patient.objects.select_for_update().get(pk=patient.pk)
            serializer.save(created_by=self.request.user)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Handle IntegrityError from duplicate mapping as 409 Conflict."""
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "This patient-doctor mapping already exists."},
                status=status.HTTP_409_CONFLICT,
            )

    def by_patient(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """GET /api/mappings/<patient_id>/ — all doctors assigned to a patient."""
        patient_id = self.kwargs.get("patient_id") or self.kwargs.get("pk", "")
        if not Patient.objects.filter(pk=patient_id, created_by=request.user).exists():  # type: ignore[misc]
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        qs = PatientDoctorMapping.objects.select_related("patient", "doctor").filter(
            patient_id=patient_id,
            created_by=request.user,  # type: ignore[misc]
        )
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
