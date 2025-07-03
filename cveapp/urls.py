"""
URL configuration for cveapp.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('api/cves/', views.CVEListApiView.as_view()),
    path('api/tracks/', views.TrackListApiView.as_view()),
    path('api/cve-summary-charts/', views.CVESummaryChartsApiView.as_view()),
]