from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsHR(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'hr'
        )


class IsApplicant(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'applicant'
        )


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'posted_by'):
            return obj.posted_by == request.user
        if hasattr(obj, 'applicant'):
            return obj.applicant == request.user
        return False


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
