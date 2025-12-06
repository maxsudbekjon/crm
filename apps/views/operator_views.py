from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics

from apps.models import Operator
from apps.serializers.operator_serializers import OperatorSerializer

CustomUser = get_user_model()

# =========================
# Operator Views
# =========================



class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin

class IsSelfOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.user == request.user


class OperatorCreateView(generics.CreateAPIView):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        request_body=OperatorSerializer,
        responses={201: OperatorSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()


class OperatorListView(generics.ListAPIView):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        responses={200: OperatorSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OperatorDetailView(generics.RetrieveUpdateAPIView):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsSelfOrAdmin]

    @swagger_auto_schema(
        responses={200: OperatorSerializer},
        request_body=OperatorSerializer
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)