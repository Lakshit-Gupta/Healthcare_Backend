"""Tests for patient API endpoints."""

import datetime

import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.patients.tests.factories import PatientFactory

PATIENTS_URL = "/api/patients/"


def detail_url(patient_id: str) -> str:
    return f"{PATIENTS_URL}{patient_id}/"


@pytest.mark.django_db
class TestPatientAPI:
    def setup_method(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_patient(self) -> None:
        response = self.client.post(
            PATIENTS_URL,
            {
                "name": "John Doe",
                "date_of_birth": "1990-01-15",
                "phone": "1234567890",
                "email": "john@example.com",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "John Doe"
        assert str(response.data["created_by"]) == str(self.user.pk)

    def test_list_patients(self) -> None:
        PatientFactory.create_batch(3, created_by=self.user)
        response = self.client.get(PATIENTS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_retrieve_patient(self) -> None:
        patient = PatientFactory(created_by=self.user)
        response = self.client.get(detail_url(str(patient.pk)))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(patient.pk)

    def test_update_patient(self) -> None:
        patient = PatientFactory(created_by=self.user)
        response = self.client.put(
            detail_url(str(patient.pk)),
            {
                "name": "Updated Name",
                "date_of_birth": "1990-01-15",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Name"

    def test_delete_patient(self) -> None:
        patient = PatientFactory(created_by=self.user)
        response = self.client.delete(detail_url(str(patient.pk)))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_ownership_isolation(self) -> None:
        """User A cannot see User B's patients."""
        other_user = UserFactory()
        PatientFactory(created_by=other_user)
        PatientFactory(created_by=self.user)

        response = self.client.get(PATIENTS_URL)
        assert response.data["count"] == 1

    def test_cannot_access_other_user_patient(self) -> None:
        other_user = UserFactory()
        patient = PatientFactory(created_by=other_user)
        response = self.client.get(detail_url(str(patient.pk)))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_filter_by_name(self) -> None:
        PatientFactory(created_by=self.user, name="Alice Smith")
        PatientFactory(created_by=self.user, name="Bob Jones")
        response = self.client.get(PATIENTS_URL, {"name": "Alice"})
        assert response.data["count"] == 1

    def test_filter_by_dob(self) -> None:
        PatientFactory(created_by=self.user, date_of_birth=datetime.date(1990, 1, 15))
        PatientFactory(created_by=self.user, date_of_birth=datetime.date(2000, 6, 1))
        response = self.client.get(PATIENTS_URL, {"date_of_birth": "1990-01-15"})
        assert response.data["count"] == 1

    def test_create_patient_missing_required_fields(self) -> None:
        response = self.client.post(PATIENTS_URL, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_patient_invalid_date_format(self) -> None:
        response = self.client.post(
            PATIENTS_URL,
            {"name": "Test", "date_of_birth": "not-a-date"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestPatientQueryCount(TestCase):
    """Verify N+1 prevention with assertNumQueries."""

    def setUp(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_no_n_plus_one(self) -> None:
        """Listing 20 patients must not exceed a fixed query count."""
        PatientFactory.create_batch(20, created_by=self.user)
        # auth is force_authenticated (0 queries), count + select = 2
        with self.assertNumQueries(2):
            response = self.client.get(PATIENTS_URL)
        assert response.status_code == status.HTTP_200_OK
