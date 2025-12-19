from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from apps.models.task_model import Task
from apps.serializers import TaskSerializer

class TaskListAPIView(ListAPIView):
    serializer_class = TaskSerializer

    # Swagger query param optional
    filter_param = openapi.Parameter(
        name='filter_by',
        in_=openapi.IN_QUERY,
        type=openapi.TYPE_STRING,
        required=False,
        description="Filter: barchasi, faol, kechiktirilgan, bajarildi"
    )

    @swagger_auto_schema(manual_parameters=[filter_param])
    def get_queryset(self):
        # Lead va course ma'lumotlarini oldindan yuklash
        queryset = Task.objects.select_related('lead', 'lead__course').all()

        filter_by = self.request.GET.get('filter_by')

        # Filterlash
        if filter_by == 'faol':
            queryset = queryset.filter(is_completed=False)
        elif filter_by == 'kechiktirilgan':
            queryset = queryset.filter(is_completed=False, deadline__lt=timezone.now())
        elif filter_by == 'bajarildi':
            queryset = queryset.filter(is_completed=True)
        # filter_by berilmasa: barcha tasks

        return queryset