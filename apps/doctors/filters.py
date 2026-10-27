"""Doctor filters."""

from django_filters import rest_framework as filters

from apps.doctors.models import Doctor


class DoctorFilter(filters.FilterSet):  # type: ignore[misc]
    """Filter doctors by specialization."""

    name = filters.CharFilter(lookup_expr="icontains")
    specialization = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Doctor
        fields = ["name", "specialization"]
