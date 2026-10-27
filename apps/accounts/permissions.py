"""Custom permissions."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request


class IsOwner(BasePermission):
    """Object-level: only the creator can access."""

    def has_object_permission(
        self, request: Request, view: object, obj: object
    ) -> bool:
        return getattr(obj, "created_by", None) == request.user
