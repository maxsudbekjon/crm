from datetime import timedelta
import datetime
from django.utils import timezone
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from rest_framework import generics, permissions, viewsets, status, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.views import APIView

from .models import *
from .serializers import *

# =========================
# Lead Views
# =========================

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


# =========================
# Operator Views
# =========================

from django.contrib.auth import get_user_model
CustomUser = get_user_model()

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


# =========================
# Task Views
# =========================

class TaskCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        request_body=TaskSerializer,
        responses={201: TaskSerializer}
    )
    def post(self, request):
        if not hasattr(request.user, 'operator'):
            raise serializers.ValidationError("Ushbu foydalanuvchiga Operator bog‘lanmagan")

        operator = request.user.operator
        serializer = TaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        deadline = serializer.validated_data.get('deadline')
        if deadline and deadline < timezone.now():
            raise serializers.ValidationError("Deadline o‘tgan sanaga o‘rnatilmasligi kerak.")

        serializer.save(operator=operator)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SoldClientsPaymentsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Response(
            description="Payment results",
            examples={"application/json": [{"lead_id": 1, "total_payment": 500000}]}
        )}
    )
    def get(self, request):
        sold_leads = Lead.objects.filter(status='sold')
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


# =========================
# Notification Views
# =========================

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
        openapi.Parameter('pk', openapi.IN_PATH, description="Notification ID", type=openapi.TYPE_INTEGER),
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


# =========================
# Operator Analytics
# =========================

@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter('operator_id', openapi.IN_QUERY, description="Analitika olish uchun operator ID", type=openapi.TYPE_INTEGER, required=True)
    ],
    operation_description="Bitta operator uchun kunlik va oylik analitika (calls, messages va o‘qiyotganlar bilan birga)",
    responses={200: openapi.Response(description="Operator analitika natijasi")}
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

    # Leadlar
    today_leads = Lead.objects.filter(operator=operator, created_at__date=today).count()
    month_leads = Lead.objects.filter(operator=operator, created_at__date__gte=month_start).count()
    today_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date=today).count()
    month_sold_leads = Lead.objects.filter(operator=operator, status="sold", created_at__date__gte=month_start).count()

    conversion_rate_today = round((today_sold_leads / today_leads) * 100, 2) if today_leads else 0
    conversion_rate_month = round((month_sold_leads / month_leads) * 100, 2) if month_leads else 0

    # Tasklar
    start = timezone.make_aware(datetime.datetime.combine(today, datetime.time.min))
    end = timezone.make_aware(datetime.datetime.combine(today, datetime.time.max))

    today_tasks_done = Task.objects.filter(operator=operator, is_completed=True, completed_at__gte=start, completed_at__lte=end).count()
    today_tasks_pending = Task.objects.filter(operator=operator, is_completed=False, deadline__gte=timezone.now()).count()
    today_tasks_overdue = Task.objects.filter(operator=operator, is_completed=False, deadline__lt=timezone.now()).count()
    month_tasks_done = Task.objects.filter(operator=operator, is_completed=True, completed_at__date__gte=month_start).count()

    # Daromad
    today_income = float(Contract.objects.filter(operator=operator, created_at__date=today).aggregate(total=Sum("amount_paid"))["total"] or 0) * 0.1
    month_income = float(Contract.objects.filter(operator=operator, created_at__date__gte=month_start).aggregate(total=Sum("amount_paid"))["total"] or 0) * 0.1

    # Calls va Messages
    today_calls = Call.objects.filter(operator=operator, created_at__date=today).count()
    today_messages = SMS.objects.filter(operator=operator, sent_at__date=today).count()
    today_call_seconds = Call.objects.filter(operator=operator, created_at__date=today).aggregate(total=Sum("duration_seconds"))["total"] or 0
    minutes = today_call_seconds // 60
    seconds = today_call_seconds % 60
    today_call_duration = f"{minutes} min {seconds} sec"

    # Jarimalar
    today_penalties = Penalty.objects.filter(operator=operator, created_at__date=today).aggregate(total_points=Sum("points"))["total_points"] or 0
    month_penalties = Penalty.objects.filter(operator=operator, created_at__date__gte=month_start).aggregate(total_points=Sum("points"))["total_points"] or 0

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
            "today_income": today_income,
            "today_penalties": today_penalties,
            "conversion_rate_today": conversion_rate_today,
        },
        "monthly": {
            "month_leads": month_leads,
            "month_sold_leads": month_sold_leads,
            "month_income": month_income,
            "month_tasks_done": month_tasks_done,
            "month_penalties": month_penalties,
            "conversion_rate_month": conversion_rate_month,
        },
    }

    return JsonResponse(result, safe=False)


@api_view(['GET'])
def analytics_api(request):
    now = timezone.now()

    # 1 hafta va 1 oy ichida sotilgan leadlar
    week_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=7)
    ).count()

    month_sold = Lead.objects.filter(
        status=Lead.Status.SOLD,
        updated_at__gte=now - timedelta(days=30)
    ).count()

    # Eng ko'p lead olgan operator
    top_operator_leads = (
        Operator.objects.annotate(lead_count=Count('leads'))
        .order_by('-lead_count')
        .values('user__username', 'lead_count')
        .first()
    )

    # Eng yaxshi sotgan operator
    top_operator_sales = (
        Operator.objects.annotate(
            sold_count=Count('leads', filter=Q(leads__status=Lead.Status.SOLD))
        )
        .order_by('-sold_count')
        .values('user__username', 'sold_count')
        .first()
    )

    overall_leads = Lead.objects.all().count()
    sold_leads = Lead.objects.filter(status=Lead.Status.SOLD).count()

    # Oxirgi 1 hafta va 1 oy ichida kelgan leadlar soni
    week_created = Lead.objects.filter(
        created_at__gte=now - timedelta(days=7)
    ).count()

    month_created = Lead.objects.filter(
        created_at__gte=now - timedelta(days=30)
    ).count()

    data = {
        "sold_last_week": week_sold,
        "sold_last_month": month_sold,
        "top_operator_by_leads": top_operator_leads,
        "top_operator_by_sales": top_operator_sales,
        "lead_created_last_week": week_created,
        "lead_created_last_month": month_created,
        "overall_leads": overall_leads,
        "sold_leads": sold_leads
    }

    return Response(data)