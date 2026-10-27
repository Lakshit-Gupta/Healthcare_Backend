"""Tests for doctor API endpoints."""

import pytest
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory
from apps.doctors.tests.factories import DoctorFactory

DOCTORS_URL = "/api/doctors/"


def detail_url(doctor_id: str) -> str:
    return f"{DOCTORS_URL}{doctor_id}/"


@pytest.mark.django_db
class TestDoctorAPI:
    def setup_method(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_create_doctor(self) -> None:
        response = self.client.post(
            DOCTORS_URL,
            {
                "name": "Dr. Smith",
                "specialization": "Cardiology",
                "phone": "9876543210",
                "email": "smith@hospital.com",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Dr. Smith"

    def test_list_doctors_returns_all(self) -> None:
        """All doctors visible to any authenticated user."""
        other_user = UserFactory()
        DoctorFactory(created_by=other_user)
        DoctorFactory(created_by=self.user)

        response = self.client.get(DOCTORS_URL)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2

    def test_retrieve_doctor(self) -> None:
        doctor = DoctorFactory(created_by=self.user)
        response = self.client.get(detail_url(str(doctor.pk)))
        assert response.status_code == status.HTTP_200_OK
        assert str(response.data["id"]) == str(doctor.pk)

    def test_update_doctor(self) -> None:
        doctor = DoctorFactory(created_by=self.user)
        response = self.client.put(
            detail_url(str(doctor.pk)),
            {"name": "Dr. Updated", "specialization": "Neurology"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Dr. Updated"

    def test_delete_doctor(self) -> None:
        doctor = DoctorFactory(created_by=self.user)
        response = self.client.delete(detail_url(str(doctor.pk)))
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_unauthenticated_access_blocked(self) -> None:
        client = APIClient()
        response = client.get(DOCTORS_URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_filter_by_specialization(self) -> None:
        DoctorFactory(created_by=self.user, specialization="Cardiology")
        DoctorFactory(created_by=self.user, specialization="Neurology")
        response = self.client.get(DOCTORS_URL, {"specialization": "Cardiology"})
        assert response.data["count"] == 1


@pytest.mark.django_db
class TestDoctorQueryCount(TestCase):
    def setUp(self) -> None:
        self.user = UserFactory()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_list_no_n_plus_one(self) -> None:
        DoctorFactory.create_batch(20, created_by=self.user)
        with self.assertNumQueries(2):
            response = self.client.get(DOCTORS_URL)
        assert response.status_code == status.HTTP_200_OK
