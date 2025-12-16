from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsAssignedOperator(permissions.BasePermission):
    """
    Faqat lead biriktirilgan operator statusni update qilishi mumkin
    """

    def has_object_permission(self, request, view, obj):
        return obj.operator == request.user.operator


class LeadListPermission(BasePermission):
    """
    Admin – barcha sold leadlarni ko‘radi
    Operator – faqat o‘zi sold qilgan leadlarni ko‘radi
    """

    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.operator == request.user