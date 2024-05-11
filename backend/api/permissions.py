from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class IsAuthenticatedAndAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or obj.author == request.user
            or request.user.is_superuser
        )


class IsAuthenticatedAndAuthor(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
