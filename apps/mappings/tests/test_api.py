"""Tests for mapping API endpoints."""

from concurrent.futures import ThreadPoolExecutor

import pytest
from django.test import TestCase, TransactionTestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.doctors.tests.factories import DoctorFactory
from apps.mappings.models import PatientDoctorMapping
from apps.patients.tests.factories import PatientFactory

MAPPINGS_URL = "/api/mappings/"


def detail_url(mapping_id: str) -> str:
    return f"{MAPPINGS_URL}{mapping_id}/"


@pytest.mark.django_db
class TestMappingAPI:
    def setup_method(self) -> None:
        self.user = UserFactory()
        self.patient = PatientFactory(created_by=self.user)
        self.doctor = DoctorFactory(created_by=self.user)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_mapping(self) -> None:
        response = self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert str(response.data["patient"]) == str(self.patient.pk)
        assert str(response.data["doctor"]) == str(self.doctor.pk)

    def test_duplicate_mapping_rejected(self) -> None:
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        response = self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    def test_cross_user_mapping_rejected(self) -> None:
        """Cannot assign doctor to another user's patient."""
        other_user = UserFactory()
        other_patient = PatientFactory(created_by=other_user)

        response = self.client.post(
            MAPPINGS_URL,
            {"patient": str(other_patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_list_mappings(self) -> None:
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        response = self.client.get(MAPPINGS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filter_by_patient_id(self) -> None:
        doctor2 = DoctorFactory(created_by=self.user)
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(doctor2.pk)},
            format="json",
        )
        response = self.client.get(MAPPINGS_URL, {"patient_id": str(self.patient.pk)})
        assert response.data["count"] == 2

    def test_delete_mapping(self) -> None:
        response = self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        mapping_id = response.data["id"]
        response = self.client.delete(detail_url(mapping_id))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_cascade_on_patient_delete(self) -> None:
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        assert PatientDoctorMapping.objects.count() == 1
        self.patient.delete()
        assert PatientDoctorMapping.objects.count() == 0

    def test_by_patient_url_returns_mappings(self) -> None:
        """GET /api/mappings/<patient_id>/ returns doctors for that patient."""
        doctor2 = DoctorFactory(created_by=self.user)
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(self.doctor.pk)},
            format="json",
        )
        self.client.post(
            MAPPINGS_URL,
            {"patient": str(self.patient.pk), "doctor": str(doctor2.pk)},
            format="json",
        )
        response = self.client.get(f"{MAPPINGS_URL}{self.patient.pk}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_by_patient_other_user_returns_404(self) -> None:
        """GET /api/mappings/<patient_id>/ for another user's patient → 404."""
        other_user = UserFactory()
        other_patient = PatientFactory(created_by=other_user)
        response = self.client.get(f"{MAPPINGS_URL}{other_patient.pk}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_by_patient_nonexistent_uuid_returns_404(self) -> None:
        """GET /api/mappings/<nonexistent_uuid>/ → 404."""
        import uuid

        fake_id = uuid.uuid4()
        response = self.client.get(f"{MAPPINGS_URL}{fake_id}/")
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestMappingQueryCount(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        patient = PatientFactory(created_by=self.user)
        for _ in range(10):
            doctor = DoctorFactory(created_by=self.user)
            PatientDoctorMapping.objects.create(
                patient=patient, doctor=doctor, created_by=self.user
            )

    def test_list_no_n_plus_one(self) -> None:
        with self.assertNumQueries(2):
            response = self.client.get(MAPPINGS_URL)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
class TestConcurrentMapping(TransactionTestCase):
    """Test select_for_update prevents duplicate concurrent mappings."""

    def test_concurrent_duplicate_mapping_rejected(self) -> None:
        user = UserFactory()
        patient = PatientFactory(created_by=user)
        doctor = DoctorFactory(created_by=user)

        def create_mapping() -> int:
            client = APIClient()
            client.force_authenticate(user=user)
            response = client.post(
                MAPPINGS_URL,
                {"patient": str(patient.pk), "doctor": str(doctor.pk)},
                format="json",
            )
            return response.status_code

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(create_mapping) for _ in range(2)]
            statuses = sorted(f.result() for f in futures)

        assert statuses == [201, 409]
