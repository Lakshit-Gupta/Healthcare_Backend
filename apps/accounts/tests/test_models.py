"""Tests for user model."""

import pytest
from django.contrib.auth import get_user_model

from apps.accounts.tests.factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self) -> None:
        user = UserFactory()
        assert user.pk is not None
        assert user.is_active is True
        assert user.is_staff is False

    def test_str(self) -> None:
        user = UserFactory(email="test@example.com")
        assert str(user) == "test@example.com"

    def test_email_is_unique(self) -> None:
        UserFactory(email="dup@example.com")
        with pytest.raises(Exception):  # noqa: B017
            UserFactory(email="dup@example.com")

    def test_uuid_pk(self) -> None:
        user = UserFactory()
        assert len(str(user.pk)) == 36  # UUID format

    def test_create_superuser(self) -> None:
        su = User.objects.create_superuser(
            email="admin@example.com", password="admin123", name="Admin"
        )
        assert su.is_staff is True
        assert su.is_superuser is True
