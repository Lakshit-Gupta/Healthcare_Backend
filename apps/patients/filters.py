"""Patient filters."""

from django_filters import rest_framework as filters

from apps.patients.models import Patient


class PatientFilter(filters.FilterSet):  # type: ignore[misc]
    """Filter patients by name or date of birth."""

    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Patient
        fields = ["name", "date_of_birth"]
