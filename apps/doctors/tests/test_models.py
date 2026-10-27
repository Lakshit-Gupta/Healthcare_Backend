"""Tests for doctor model."""

import pytest

from apps.doctors.tests.factories import DoctorFactory


@pytest.mark.django_db
class TestDoctorModel:
    def test_str(self) -> None:
        doctor = DoctorFactory(name="Dr. Smith", specialization="Cardiology")
        assert str(doctor) == "Dr. Smith (Cardiology)"

    def test_timestamps_auto_set(self) -> None:
        doctor = DoctorFactory()
        assert doctor.created_at is not None
        assert doctor.updated_at is not None

    def test_uuid_pk(self) -> None:
        doctor = DoctorFactory()
        assert len(str(doctor.pk)) == 36
