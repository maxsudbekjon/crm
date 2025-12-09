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
    path('leads/', LeadListView.as_view(), name='lead-list'),
    path('leads/<int:pk>/update-status/', LeadStatusUpdateAPIView.as_view(), name='lead-update-status'),
    path('leads/sold/', SoldLeadsAPIView.as_view(), name='sold-leads'),

    path('tasks/create/', TaskCreateAPIView.as_view(), name='task-create'),
    path('tasks/list/', TaskListAPIView.as_view(), name='task-list'),
    path('Payment/Create/', PaymentCreateAPIView.as_view(), name='payemnt-create'),

    # Task create endpoint (viewset bilan ishlatilmaydigan alohida)
    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    path('notifications/read/', mark_notification_read, name='notification-read'),

    #operator_analytics urls
    path('operator_analytics/', operator_analytics, name='operator_analytics'),
    path('overall_analitic/',  analytics_api, name='overall_analitic'),

    # Router bilan viewsetlar
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

