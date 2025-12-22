from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Swagger va ReDoc uchun schema view
schema_view = get_schema_view(
   openapi.Info(
      title="IT House Academy API",
      default_version='v1',
      description="API hujjatlari",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@yourapi.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # API
    path('api/', include('apps.urls')),
    path('api/auth/', include('Auth.urls')),

    # Docs
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]