from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminForUnsafe(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_admin)


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user or getattr(request.user, "is_admin", False)


class IsHotelOwnerForRoom(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.hotel.owner == request.user or getattr(request.user, "is_admin", False)


class IsObjectUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or getattr(request.user, "is_admin", False)


class IsObjectUserOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user or getattr(request.user, "is_admin", False)
