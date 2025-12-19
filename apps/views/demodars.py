from rest_framework import generics, permissions
from apps.models.demodars import DemoLesson, LeadDemoAssignment
from apps.serializers import DemoLessonSerializer, LeadDemoAssignmentSerializer

# =========================
# Kursdagi barcha demo darslarni ko'rish (faol darslar)
# =========================
class DemoLessonListView(generics.ListAPIView):
    serializer_class = DemoLessonSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Faqat faol demo darslarni olib kelamiz
        return DemoLesson.objects.filter(is_active=True).select_related('teacher')


# =========================
# Leadga demo dars biriktirish
# =========================
class LeadDemoAssignmentCreateView(generics.CreateAPIView):
    queryset = LeadDemoAssignment.objects.all()
    serializer_class = LeadDemoAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        # assigned_by maydonini avtomatik request.user bilan to'ldiramiz
        serializer.save(assigned_by=self.request.user)