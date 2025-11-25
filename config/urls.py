from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from apps.views import LeadCreateAPIView, lead_source_stats
from apps.views import react_app

schema_view = get_schema_view(
   openapi.Info(
      title="IT House",
      default_version='v1',
      description="API documentation for IT House Academy",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)
urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),
    path('api/', include('apps.urls')),
    path('api/', include('user.urls')),

    path('analyticss/lead-source/', lead_source_stats, name='lead-source-stats'),


    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path("instagram/", react_app),
    path('social-user/', include('social_django.urls', namespace='social')),
    path('analyticss/', include('analytics.urls')),

    path("", react_app),

]