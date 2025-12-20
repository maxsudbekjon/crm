from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.models import Lead
from apps.permissions import IsAssignedOperator
from apps.serializers import LeadSearchSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


@swagger_auto_schema(
    method='get',
    manual_parameters=[
        openapi.Parameter(
            'q',
            openapi.IN_QUERY,
            description="Lead full_name bo‘yicha qidirish",
            type=openapi.TYPE_STRING
        )
    ]
)
@api_view(["GET"])
@permission_classes([IsAuthenticated, IsAssignedOperator])
def lead_search_api(request):
    query = request.query_params.get("q", "")
    leads_qs = Lead.objects.all()

    if query:
        # Case-insensitive exact match ham mumkin:
        leads_qs = leads_qs.filter(full_name__icontains=query)

    serializer = LeadSearchSerializer(leads_qs, many=True)
    return Response({"results": serializer.data})