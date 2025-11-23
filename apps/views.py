from django.utils import timezone
from django.db.models import Sum
from django.http import JsonResponse
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import serializers
from .models import Lead, Task, Operator, Notification, Contract, SMS, Penalty
from .serializers import *

# ==========================
# Lead Views
# ==========================

class LeadCreateView(generics.CreateAPIView):
    serializer_class = LeadCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=LeadCreateSerializer,
        responses={201: LeadSerializer}
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(operator=self.request.user.operator)


class LeadListView(generics.ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: LeadSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        operator = getattr(self.request.user, 'operator', None)
        if not operator:
            return Lead.objects.none()
        return Lead.objects.filter(operator=operator)


class LeadUpdateStatusView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=LeadStatusUpdateSerializer,
        responses={200: LeadSerializer}
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def get_queryset(self):
        operator = getattr(self.request.user, 'operator', None)
        if not operator:
            return Lead.objects.none()
        return Lead.objects.filter(operator=operator)


# ==========================
# Operator Views
# ==========================

from rest_framework import generics, permissions
from .models import Operator
from .serializers import OperatorSerializer
from django.contrib.auth import get_user_model

CustomUser = get_user_model()


# --- PERMISSIONS ---
class IsAdmin(permissions.BasePermission):
    """Faqat admin uchun ruxsat"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsSelfOrAdmin(permissions.BasePermission):
    """Admin – hamma operatorlarni update qila oladi
       Operator – faqat o‘z profilini update qila oladi
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        return obj.user == request.user


# --- CREATE OPERATOR (faqat admin) ---
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


# --- LIST ALL OPERATORS (faqat admin) ---
class OperatorListView(generics.ListAPIView):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAdmin]

    @swagger_auto_schema(
        responses={200: OperatorSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# --- RETRIEVE & UPDATE OPERATOR PROFILE ---
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



# ==========================
# Task Views
# ==========================

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, serializers
from django.utils import timezone

from .models import Task, Lead
from .serializers import TaskSerializer


class TaskCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        print("Token:", request.headers.get("Authorization"))
        print("Kelgan user:", request.user)

        # Operator borligini tekshirish
        if not hasattr(request.user, 'operator'):
            raise serializers.ValidationError("Ushbu foydalanuvchiga Operator bog‘lanmagan")

        operator = request.user.operator

        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Deadline validatsiyasi
        deadline = serializer.validated_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise serializers.ValidationError("Deadline o‘tgan sanaga o‘rnatilmasligi kerak.")

        # Task yaratish
        serializer.save(operator=operator)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


from django.db.models import Sum


class SoldClientsPaymentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Payment results",
            examples={"application/json": [{"lead_id": 1, "total_payment": 500000}]}
        )}
    )

    def get(self, request):
        sold_leads = Lead.objects.filter(status='sotildi')
        results = []

        for lead in sold_leads:
            total_payment = lead.payment_set.aggregate(total=Sum('amount'))['total'] or 0

            operator = lead.operator
            operator_bonus = operator.salary * 0.1 if operator and hasattr(operator, 'salary') else 0

            results.append({
                'lead_id': lead.id,
                'lead_name': lead.full_name,
                'total_payment': total_payment,
                'operator_id': operator.id if operator else None,
                'operator_name': operator.full_name if operator else None,
                'operator_bonus': operator_bonus
            })

        return Response(results, status=status.HTTP_200_OK)


# ==========================
# Notification Views
# ==========================

class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')


@swagger_auto_schema(
    method='post',
    manual_parameters=[
        openapi.Parameter(
            'pk',
            openapi.IN_PATH,
            description="Notification ID",
            type=openapi.TYPE_INTEGER
        ),
    ],
    responses={200: openapi.Response('Notification marked as read')}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    try:
        notif = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return Response({"detail": "Not found"}, status=404)
    notif.is_read = True
    notif.save(update_fields=['is_read'])
    return Response({"ok": True})

# ==========================
# Operator_analytics
# ==========================
from rest_framework.decorators import api_view
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import datetime
from .models import Operator, Lead, Task, Contract, Penalty, SMS, Call


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'operator_id',
            openapi.IN_QUERY,
            description="Analitika olish uchun operator ID",
            type=openapi.TYPE_INTEGER,
            required=True
        ),
    ],
    operation_description="Bitta operator uchun kunlik va oylik analitika (calls, messages va o‘qiyotganlar bilan birga)",
    responses={
        200: openapi.Response(
            description="Operator analitika natijasi",
            examples={
                "application/json": {
                    "operator": "Ali Valiyev",
                    "branch": "Toshkent Filiali",
                    "daily": {
                        "today_leads": 5,
                        "today_sold_leads": 2,
                        "calls": 3,
                        "messages": 4,
                        "today_tasks_done": 4,
                        "today_tasks_pending": 2,
                        "today_tasks_overdue": 1,
                        "today_income": 1200000,
                        "today_penalties": 2,
                        "conversion_rate": 40.0
                    },
                    "monthly": {
                        "month_leads": 50,
                        "month_sold_leads": 18,
                        "month_income": 13000000,
                        "month_tasks_done": 35,
                        "month_penalties": 5
                    }
                }
            }
        )
    }
)
@api_view(['GET'])
def operator_analytics(request):
    operator_id = request.GET.get('operator_id')
    if not operator_id:
        return JsonResponse({"error": "operator_id parametri kerak"}, status=400)

    try:
        operator = Operator.objects.get(id=operator_id)
    except Operator.DoesNotExist:
        return JsonResponse({"error": "Operator topilmadi"}, status=404)

    today = timezone.now().date()
    month_start = today.replace(day=1)

    # === Leadlar ===
    today_leads = Lead.objects.filter(operator=operator, created_at__date=today).count()
    month_leads = Lead.objects.filter(operator=operator, created_at__date__gte=month_start).count()

    # 🔹 Bugun va oy davomida sotilgan leadlar (o‘qiyotganlar)
    today_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date=today).count()
    month_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date__gte=month_start).count()

    # === Kunlik conversion rate ===
    conversion_rate_today = (
        round((today_sold_leads / today_leads) * 100, 2)
        if today_leads else 0
    )

    # === Oylik conversion rate ===
    conversion_rate_month = (
        round((month_sold_leads / month_leads) * 100, 2)
        if month_leads else 0
    )

    # === Tasklar ===
    start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

    today_tasks_done = Task.objects.filter(
        operator=operator,
        is_completed=True,
        completed_at__gte=start,
        completed_at__lte=end
    ).count()

    today_tasks_pending = Task.objects.filter(
        operator=operator,
        is_completed=False,
        deadline__gte=timezone.now()
    ).count()

    today_tasks_overdue = Task.objects.filter(
        operator=operator,
        is_completed=False,
        deadline__lt=timezone.now()
    ).count()

    month_tasks_done = Task.objects.filter(
        operator=operator,
        is_completed=True,
        completed_at__date__gte=month_start
    ).count()

    # === Daromad (umumiydan 10%) ===
    today_income = (
        Contract.objects.filter(operator=operator, created_at__date=today)
        .aggregate(total=Sum("amount_paid"))["total"] or 0
    )
    today_income = float(today_income) * 0.1  # faqat 10% qismini olamiz

    month_income = (
        Contract.objects.filter(operator=operator, created_at__date__gte=month_start)
        .aggregate(total=Sum("amount_paid"))["total"] or 0
    )
    month_income = float(month_income) * 0.1  # oylik daromadning 10% i


    # === Aloqa turlari (calls, messages) ===
    today_calls = Call.objects.filter(operator=operator, created_at__date=today).count()
    today_messages = SMS.objects.filter(operator=operator, sent_at__date=today).count()
    # === Bugun qancha vaqt gaplashgan (total call duration) ===
    today_call_seconds = Call.objects.filter(
        operator=operator,
        created_at__date=today
    ).aggregate(total=Sum("duration_seconds"))["total"] or 0

    minutes = today_call_seconds // 60
    seconds = today_call_seconds % 60
    today_call_duration = f"{minutes} min {seconds} sec"

    # === Jarimalar ===
    today_penalties = Penalty.objects.filter(operator=operator, created_at__date=today).aggregate(
        total_points=Sum("points")
    )["total_points"] or 0

    month_penalties = Penalty.objects.filter(operator=operator, created_at__date__gte=month_start).aggregate(
        total_points=Sum("points")
    )["total_points"] or 0


    # === Natija ===
    result = {
        "operator": operator.user.full_name,
        "branch": operator.branch.name,
        "daily": {
            "today_leads": today_leads,
            "today_sold_leads": today_sold_leads,
            "calls": today_calls,
            "today_call_duration": today_call_duration,
            "messages": today_messages,
            "today_tasks_done": today_tasks_done,
            "today_tasks_pending": today_tasks_pending,
            "today_tasks_overdue": today_tasks_overdue,
            "today_income": float(today_income),
            "today_penalties": today_penalties,
            "conversion_rate_today": conversion_rate_today,
        },
        "monthly": {
            "month_leads": month_leads,
            "month_sold_leads": month_sold_leads,
            "month_income": float(month_income),
            "month_tasks_done": month_tasks_done,
            "month_penalties": month_penalties,
            "conversion_rate_month": conversion_rate_month,
        },
    }

    return JsonResponse(result, safe=False)
