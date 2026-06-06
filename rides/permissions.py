from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Only users with the admin role can call this endpoint."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "role", None) == "admin"
        )