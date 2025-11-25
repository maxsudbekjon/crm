from django.urls import path
from . import views

urlpatterns = [
    path("track-click/", views.track_click, name="track_click"),
    path("lead-form/", views.lead_form, name="lead_form"),
    path("thanks/", views.thanks, name="thanks"),
    path("stats/", views.stats_page, name="stats_page"),
    path("stats-json/", views.click_stats, name="click_stats_json"),
]