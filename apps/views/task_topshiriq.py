from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination

from apps.models.task_model import Task
from apps.serializers.task_topshiriq import TaskSerializer


class TaskPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50


class TaskListAPIView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TaskPagination

    @swagger_auto_schema(
        operation_summary="Operator topshiriqlari",
        operation_description="barchasi / faol / kechiktirilgan / bajarildi",
        manual_parameters=[
            openapi.Parameter(
                name='filter_by',
                in_=openapi.IN_PATH,  # IN_PATH bo'lishi kerak!
                type=openapi.TYPE_STRING,
                enum=['barchasi', 'faol', 'kechiktirilgan', 'bajarildi'],
                required=True,
                description="Filter: barchasi, faol, kechiktirilgan, bajarildi"
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        now = timezone.now()

        filter_by = self.request.query_params.get('filter_by', 'barchasi').strip().lower()

        if hasattr(user, 'operator') and user.operator is not None:
            queryset = Task.objects.filter(operator=user.operator)
        else:
            queryset = Task.objects.all()

        queryset = queryset.exclude(deadline__isnull=True)
        queryset = queryset.order_by('-deadline', '-created_at')

        if filter_by == "bajarildi":
            queryset = queryset.filter(is_completed=True)
        elif filter_by == "kechiktirilgan":
            queryset = queryset.filter(is_completed=False, deadline__lt=now)
        elif filter_by == "faol":
            queryset = queryset.filter(is_completed=False, deadline__gte=now)

        return queryset