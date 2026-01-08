from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.models.task_model import Task
from apps.serializers.task_serializers import TaskSerializer



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

