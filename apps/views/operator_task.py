from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.models.task_model import Task
from apps.serializers.task_serializers import TaskSerializer


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


class OperatorTaskListView(ListAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        operator = getattr(self.request.user, "operator", None)
        if not operator:
            return Task.objects.none()

        # status path param orqali keladi
        status_param = self.kwargs.get("status", "").strip().lower()
        now = timezone.now()

        queryset = Task.objects.filter(operator=operator).order_by('-deadline')

        if status_param == "faol":
            return queryset.filter(is_completed=False, deadline__gte=now)
        elif status_param == "bajarildi":
            return queryset.filter(is_completed=True)

        return queryset