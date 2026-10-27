"""Mapping URL routes."""

from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.mappings.views import MappingViewSet

router = DefaultRouter()
router.register("mappings", MappingViewSet, basename="mapping")

urlpatterns = [
    # GET /api/mappings/<patient_id>/ — must come before router detail route
    path(
        "mappings/<uuid:patient_id>/",
        MappingViewSet.as_view({"get": "by_patient", "delete": "destroy"}),
        name="mapping-by-patient",
    ),
    *router.urls,
]
