from rest_framework import permissions

class IsAssignedOperator(permissions.BasePermission):
    """
    Faqat lead biriktirilgan operator statusni update qilishi mumkin
    """

    def has_object_permission(self, request, view, obj):
        return obj.operator == request.user.operator
