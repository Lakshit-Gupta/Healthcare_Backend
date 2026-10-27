"""Tests for auth API endpoints."""

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.tests.factories import UserFactory

REGISTER_URL = "/api/auth/register/"
LOGIN_URL = "/api/auth/login/"
TEST_PASSWORD = "strongpass123"


@pytest.mark.django_db
class TestRegisterAPI:
    def setup_method(self) -> None:
        self.client = APIClient()

    def test_register_success(self) -> None:
        response = self.client.post(
            REGISTER_URL,
            {"email": "new@example.com", "name": "New User", "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == "new@example.com"
        assert "password" not in response.data

    def test_register_duplicate_email(self) -> None:
        UserFactory(email="dup@example.com")
        response = self.client.post(
            REGISTER_URL,
            {"email": "dup@example.com", "name": "Dup", "password": TEST_PASSWORD},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self) -> None:
        response = self.client.post(
            REGISTER_URL,
            {"email": "short@example.com", "name": "Short", "password": "123"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_fields(self) -> None:
        response = self.client.post(REGISTER_URL, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    def setup_method(self) -> None:
        self.client = APIClient()
        self.user = UserFactory(email="login@example.com")

    def test_login_success(self) -> None:
        response = self.client.post(
            LOGIN_URL,
            {"email": "login@example.com", "password": "testpass123"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "login@example.com"

    def test_login_wrong_password(self) -> None:
        response = self.client.post(
            LOGIN_URL,
            {"email": "login@example.com", "password": "wrongpass"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_AUTHENTICATION_CLASSES": [
                "rest_framework_simplejwt.authentication.JWTAuthentication",
            ],
            "DEFAULT_PERMISSION_CLASSES": [
                "rest_framework.permissions.IsAuthenticated",
            ],
            "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
            "PAGE_SIZE": 20,
            "DEFAULT_RENDERER_CLASSES": ["apps.core.renderers.ORJSONRenderer"],
            "DEFAULT_PARSER_CLASSES": ["apps.core.parsers.ORJSONParser"],
            "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        }
    )
    def test_access_without_token(self) -> None:
        response = self.client.get("/api/patients/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
