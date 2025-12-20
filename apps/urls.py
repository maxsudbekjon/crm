from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.conf.urls.static import static
from config import settings
from .views import *

app_name = "apps"

# DRF router bilan viewsetlar
router = DefaultRouter()
urlpatterns = [
    #operator
    path('operator-create/', OperatorCreateView.as_view(), name='operator-create'),
    path('OperatorList/', OperatorListView.as_view(), name='operator-list'),
    path('OperatorDetail/<int:pk>/', OperatorDetailView.as_view(), name='operator-detail'),
    path('Operator/salaries/', OperatorSalaryListAPIView.as_view(), name='operator-salaries'),
    # Lead endpoints
    path('leads/create/', LeadCreateView.as_view(), name='lead-create'),
    path('leads/<int:pk>/update-status/', LeadStatusUpdateAPIView.as_view(), name='lead-update-status'),
    path('leads/sold/', SoldLeadsAPIView.as_view(), name='sold-leads'),
    path("leads/filter/<str:period>/", LeadFilterAPIView.as_view()),

    path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/filter/<str:filter_by>/', TaskListAPIView.as_view(), name='task-list-filter'),
    path('Payment/Create/', PaymentCreateAPIView.as_view(), name='payemnt-create'),

    # Task create endpoint (viewset bilan ishlatilmaydigan alohida)
    path('notifications/list/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/create/', mark_notification_read, name='notification-read'),

    #operator_analytics urls
    path('operator_analytics/', operator_analytics, name='operator_analytics'),
    path("dashboard/direktor/", OperatorsDashboardAPIView.as_view()),
    path('dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    path("operator/statistics/", OperatorStatisticsAPIView.as_view(), name="operator-statistics"),
    path("direktor/statistics/", DirectorStatisticsAPIView.as_view(), name="director-statistics"),
    path('Direktor/Hisobotlar/',  analytics_api, name='overall_analitic'),
    path("calls/", CallsAPIView.as_view(), name='All-calls'),

    # Leadga demo dars biriktirish
    path('demo-lessons/', DemoLessonListView.as_view(), name='demo-lessons-list'),
    path('assign-demo/', LeadDemoAssignmentCreateView.as_view(), name='assign-demo'),

    path("Jamoa/", JamoaAPIView.as_view(),name="Jamoa"),
    path('source_convertion/', source_conversion_api, name='source_convertion'),
    path('weekly_dynamics/', weekly_dynamics_api, name='weekly_dynamics'),

    # Router bilan viewsetlar
    path('', include(router.urls)),
    path("leads_history/<int:lead_id>/", LeadHistoryView.as_view()),

    path("my-calls/", MyCallsAPIView.as_view()),
    path("barcha-leadlar/", DirectorStatistics.as_view(), name='barcha-leadlar'),

    # Router bilan viewsetlar
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

