"""Tests for patient model."""

import pytest

from apps.patients.tests.factories import PatientFactory


@pytest.mark.django_db
class TestPatientModel:
    def test_str(self) -> None:
        patient = PatientFactory(name="Jane Doe")
        assert str(patient) == "Jane Doe"

    def test_timestamps_auto_set(self) -> None:
        patient = PatientFactory()
        assert patient.created_at is not None
        assert patient.updated_at is not None

    def test_uuid_pk(self) -> None:
        patient = PatientFactory()
        assert len(str(patient.pk)) == 36

    def test_ordering(self) -> None:
        from apps.patients.models import Patient

        assert Patient._meta.ordering == ["-created_at"]
