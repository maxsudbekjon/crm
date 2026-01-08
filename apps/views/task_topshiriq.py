from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.models.task_model import Task
from apps.serializers.task_topshiriq import TaskSerializer


class TaskListAPIView(ListAPIView):
    serializer_class = TaskSerializer

    FILTER_OPTIONS = ['barchasi', 'faol', 'bajarildi']

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'filter_by',
                openapi.IN_QUERY,
                description="Filter variantini tanlang",
                type=openapi.TYPE_STRING,
                enum=FILTER_OPTIONS,
                required=False,
                default='barchasi'
            )
        ]
    )
    def get_queryset(self):
        # 🔹 Swagger render paytida bo‘sh queryset
        if getattr(self, 'swagger_fake_view', False):
            return Task.objects.none()

        queryset = Task.objects.select_related(
            'lead',
            'lead__course',
            'operator'
        )

        filter_by = self.request.query_params.get('filter_by', 'barchasi')

        if filter_by == 'faol':
            queryset = queryset.filter(
                is_completed=False,
                deadline__gte=timezone.now()
            )
        elif filter_by == 'bajarildi':
            queryset = queryset.filter(is_completed=True)

        return queryset