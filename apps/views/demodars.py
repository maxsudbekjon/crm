from rest_framework import generics, permissions
from apps.models.demodars import DemoLesson, LeadDemoAssignment
from apps.serializers import DemoLessonSerializer, LeadDemoAssignmentSerializer

# Kursdagi barcha demo darslarni ko'rish
class DemoLessonListView(generics.ListAPIView):
    queryset = DemoLesson.objects.filter(is_active=True)
    serializer_class = DemoLessonSerializer
    permission_classes = [permissions.IsAuthenticated]


# Leadga demo dars biriktirish
class LeadDemoAssignmentCreateView(generics.CreateAPIView):
    queryset = LeadDemoAssignment.objects.all()
    serializer_class = LeadDemoAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]