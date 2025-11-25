from django.urls import path, include
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from django.urls import path
from config import settings
from .views import LeadUpdateStatusView, TaskViewSet, LeadViewSet, success, register, LeadCreateView, OperatorViewSet
from . import views

router = DefaultRouter()
router.register(r'operators', OperatorViewSet)

router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'leads', LeadViewSet, basename='lead')

urlpatterns = [
    path('lead/<int:pk>/update-status/', LeadUpdateStatusView.as_view(), name='lead-update-status'),

    path('', include(router.urls)),
    path('accounts/', include('allauth.socialaccount.urls')),
    path('register/', register, name='register'),

    path('success/', success, name='success'),
    path('apply/', LeadCreateView.as_view(), name='lead-apply'),




]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)