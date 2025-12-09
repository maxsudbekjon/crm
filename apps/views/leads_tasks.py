from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status

from apps.models import Lead
from apps.serializers.lead_serializers import LeadCreateSerializer, LeadSerializer, LeadStatusUpdateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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


class LeadStatusUpdateAPIView(APIView):
    """
    Update Lead status.
    Only the assigned operator can update the status.
    """
    permission_classes = [permissions.IsAuthenticated]
    @swagger_auto_schema(
        request_body=LeadStatusUpdateSerializer,
        responses={200: LeadSerializer}
    )

    def patch(self, request, pk):
        lead = get_object_or_404(Lead, pk=pk)
        if lead.operator is None or lead.operator.user != request.user:
            return Response(
                {"detail": "You are not allowed to update the status of this lead."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = LeadStatusUpdateSerializer(lead, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                "message": "Lead status successfully updated.",
                "lead": serializer.data
            },
            status=status.HTTP_200_OK
        )


from rest_framework import generics, permissions
from apps.models import Lead
from apps.serializers import LeadSerializer
from apps.permissions import LeadListPermission


class SoldLeadsAPIView(generics.ListAPIView):
    serializer_class = LeadSerializer
    permission_classes = [permissions.IsAuthenticated, LeadListPermission]

    def get_queryset(self):
        qs = Lead.objects.all()

        # Admin — hammasini ko‘radi
        if self.request.user.is_staff:
            return qs.filter(status="sold")

        # Operator — faqat o'ziga tegishli sold leadlar
        return qs.filter(
            operator__user=self.request.user,   # <— Asosiy tuzatish
            status="sold"
        )