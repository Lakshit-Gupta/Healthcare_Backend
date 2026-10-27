"""Tests for custom permissions."""

import pytest
from rest_framework.test import APIRequestFactory

from apps.accounts.permissions import IsOwner
from apps.accounts.tests.factories import UserFactory


@pytest.mark.django_db
class TestIsOwnerPermission:
    def setup_method(self) -> None:
        self.permission = IsOwner()
        self.factory = APIRequestFactory()

    def test_owner_granted(self) -> None:
        user = UserFactory()
        request = self.factory.get("/")
        request.user = user

        class FakeObj:
            created_by = user

        assert self.permission.has_object_permission(request, None, FakeObj()) is True  # type: ignore[arg-type]

    def test_non_owner_denied(self) -> None:
        owner = UserFactory()
        other = UserFactory()
        request = self.factory.get("/")
        request.user = other

        class FakeObj:
            created_by = owner

        assert self.permission.has_object_permission(request, None, FakeObj()) is False  # type: ignore[arg-type]
