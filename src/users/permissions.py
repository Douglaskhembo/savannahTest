from rest_framework import permissions
from django.contrib.auth import get_user_model
from src.orders.models import Order

User = get_user_model()


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == User.Role.ADMIN:
            return True

        if isinstance(obj, User):
            return obj == request.user

        if isinstance(obj, Order):
            return obj.customer == request.user

        return False
