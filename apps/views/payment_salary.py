from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from apps.models import OperatorMonthlySalary
from apps.serializers import  PaymentCreateSerializer, OperatorSalarySerializer
from apps.utils import first_day_of_month
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiRequest
from apps.serializers import PaymentCreateSerializer
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class PaymentCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdmin]

    @swagger_auto_schema(
        operation_summary="Payment yaratish",
        operation_description="Faqat Admin foydalanuvchilar Payment yarata oladi.",
        request_body=PaymentCreateSerializer,
        responses={
            201: openapi.Response(
                description="Payment yaratildi",
                schema=PaymentCreateSerializer
            ),
            403: openapi.Response(
                description="Ruxsat yo‘q",
                examples={
                    "application/json": {
                        "detail": "You do not have permission to perform this action."
                    }
                }
            ),
        },
    )
    def post(self, request):
        serializer = PaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()

        return Response(
            {
                "message": "Payment muvaffaqiyatli yaratildi.",
                "payment": PaymentCreateSerializer(payment).data
            },
            status=status.HTTP_201_CREATED
        )

class OperatorSalaryListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # 🔥 Operator – faqat o‘zini ko‘radi
        if not request.user.is_admin:
            salaries = OperatorMonthlySalary.objects.filter(operator=request.user)
        else:
            salaries = OperatorMonthlySalary.objects.all()

        serializer = OperatorSalarySerializer(salaries, many=True)
        return Response(serializer.data)