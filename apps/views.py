from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.db.models import Sum, Count
from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from .forms import EnrollmentForm
from django.shortcuts import redirect
from .models import Enrollment


from .models import Lead, Task, Operator
from .serializers import (
    LeadSerializer,
    LeadCreateSerializer,
    LeadStatusUpdateSerializer,
    OperatorSerializer,
    TaskSerializer, TaskCreateSerializer,
)
from .forms import LeadForm


# =============================
# FRONTEND (React Fallback)
# =============================
def react_app(request):
    return render(request, "index.html")


# =============================
# FORM VIEWS
# =============================
def apply(request, source):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = source
            lead.save()
            return redirect('success')
    else:
        form = LeadForm()

    return render(request, 'register.html', {'form': form, 'source': source})


def register(request):
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("success")
    else:
        form = LeadForm()

    return render(request, "register.html", {"form": form})


def success(request):
    return render(request, "success.html")


# =============================
# LEAD API – Create (Referer Source)
# =============================
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import IntegrityError




class LeadCreateAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LeadCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

from .tasks import process_lead_commission

def add_enrollment_view(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            # Celery taskni chaqirish
            print_enrollment_id.delay(enrollment.id)  # To'g'ri Celery vazifasi chaqiriladi
            return redirect('enrollment_list')


def create_enrollment_backend(request, enrollment_id):
    """
    Bu view orqali backenddan enrollment qo'shish va
    avtomatik commission taskni ishga tushirish.
    """
    enrollment = Enrollment.objects.get(id=enrollment_id)
    process_lead_commission.delay(enrollment.id)
    return redirect('enrollment_list')

# =============================
# LEAD CRUD (ModelViewSet)
# =============================
class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [AllowAny]


# =============================
# LEAD STATUS UPDATE (Operator Only)
# =============================
class LeadUpdateStatusView(generics.UpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        operator = getattr(self.request.user, "operator", None)
        if not operator:
            return Lead.objects.none()
        return Lead.objects.filter(operator=operator)



# OPERATOR API
class OperatorViewSet(viewsets.ModelViewSet):
    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer
    permission_classes = [IsAdminUser]  # Kirish huquqlari



# TASK API
class TaskCreateView(generics.CreateAPIView):
    serializer_class = TaskCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        operator = getattr(self.request.user, "operator", None)
        if operator is None:
            raise Exception("Siz operator emassiz!")
        serializer.save(operator=operator)


class LeadCreateView(generics.CreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadCreateSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"])
    def sold_clients_payments(self, request):
        sold_leads = Lead.objects.filter(status="sotildi")
        results = []

        for lead in sold_leads:
            total_payment = lead.payment_set.aggregate(total=Sum("amount"))["total"] or 0
            operator = lead.operator
            operator_bonus = operator.salary * 0.1

            results.append({
                "lead_id": lead.id,
                "lead_name": lead.full_name,
                "total_payment": total_payment,
                "operator_id": operator.id,
                "operator_name": operator.full_name,
                "operator_bonus": operator_bonus,
            })

        return Response(results)


# ANALYTICS
@api_view(["GET"])
def lead_source_stats(request):
    data = Lead.objects.values("source").annotate(count=Count("id")).order_by("-count")
    return Response(data)