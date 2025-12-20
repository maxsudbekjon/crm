from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.models.task_model import Task
from apps.serializers.task_topshiriq import TaskSerializer

class TaskListAPIView(ListAPIView):
    serializer_class = TaskSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='filter_by',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=False,
                default='barchasi',
                enum=['barchasi', 'faol', 'kechiktirilgan', 'bajarildi'],
                description="Task holati bo‘yicha filter"
            )
        ],
        responses={200: TaskSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Task.objects.select_related('lead', 'lead__course', 'operator')
        filter_by = self.request.query_params.get('filter_by', 'barchasi')

        if filter_by == 'faol':
            queryset = queryset.filter(is_completed=False)
        elif filter_by == 'kechiktirilgan':
            queryset = queryset.filter(
                is_completed=False,
                deadline__lt=timezone.localtime(timezone.now())
            )
        elif filter_by == 'bajarildi':
            queryset = queryset.filter(is_completed=True)

        return queryset
