from django.urls import path
from apps.views  import analytics_api

urlpatterns = [
    path('overall_analitic/',  analytics_api, name='overall_analitic'),
]