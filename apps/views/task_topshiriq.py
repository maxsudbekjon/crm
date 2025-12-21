from rest_framework.generics import ListAPIView
from django.utils import timezone
from apps.models.task_model import Task
from apps.serializers.task_topshiriq import TaskSerializer


class TaskListAPIView(ListAPIView):
    serializer_class = TaskSerializer

    def get_queryset(self):
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
