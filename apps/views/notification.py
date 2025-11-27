from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response

from apps.models import Notification
from apps.serializers.task_serializers import NotificationSerializer


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

