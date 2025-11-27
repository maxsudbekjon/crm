from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions

from apps.models import Lead
from apps.serializers.lead_serializers import LeadCreateSerializer, LeadSerializer, LeadStatusUpdateSerializer


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

