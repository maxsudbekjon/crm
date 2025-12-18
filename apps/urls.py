from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    OperatorCreateView, OperatorListView, OperatorDetailView,
    OperatorSalaryListAPIView, LeadCreateView, LeadListView,
    LeadStatusUpdateAPIView, SoldLeadsAPIView, TaskCreateAPIView,
    PaymentCreateAPIView, NotificationListView,
    mark_notification_read, operator_analytics, analytics_api
)
from apps.views.demodars import DemoLessonListView, LeadDemoAssignmentCreateView
from apps.views.operator_status import OperatorStatsAPIView
from apps.views.lead_filter import LeadFilterAPIView
from apps.views.call_qongiroq import MyCallsAPIView
from rest_framework.routers import DefaultRouter

from .views.dashboard import DashboardMonthlyAPIView
from .views.operator_dashboard import OperatorsDashboardAPIView
from .views.task_topshiriq import TaskListAPIView

urlpatterns = [
    # operator
    path('operator-create/', OperatorCreateView.as_view()),
    path('operator-list/', OperatorListView.as_view()),
    path('operator/<int:pk>/', OperatorDetailView.as_view()),
    path('operator/salaries/', OperatorSalaryListAPIView.as_view()),

    # lead
    path('leads/create/', LeadCreateView.as_view()),
    path('leads/', LeadListView.as_view()),
    path('leads/<int:pk>/update-status/', LeadStatusUpdateAPIView.as_view()),
    path('leads/sold/', SoldLeadsAPIView.as_view()),

    path("leads/filter/<str:period>/", LeadFilterAPIView.as_view()),

    path('tasks/filter/<str:filter_by>/', TaskListAPIView.as_view(), name='task-list-filter'),

    path("calls/my/", MyCallsAPIView.as_view()),

    path("dashboard/operators/", OperatorsDashboardAPIView.as_view()),
    path("dashboard/status/", DashboardMonthlyAPIView.as_view()),

    path("operator/stats/", OperatorStatsAPIView.as_view(),name="operator-stats"),

    # tasks
    path('tasks/create/', TaskCreateAPIView.as_view()),

    # payment
    path('payment/create/', PaymentCreateAPIView.as_view()),

    path('demo-lessons/', DemoLessonListView.as_view(), name='demo-lessons-list'),


    # Leadga demo dars biriktirish
    path('assign-demo/', LeadDemoAssignmentCreateView.as_view(), name='assign-demo'),


    # notifications
    path('notifications/', NotificationListView.as_view()),
    path('notifications/read/', mark_notification_read),

    # analytics
    path('operator-analytics/', operator_analytics),
    path('overall-analytic/', analytics_api),


]