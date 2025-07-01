from rest_framework import routers
from cveapp.views import HostViewSet, CVEViewSet, TrackViewSet
from django.urls import path, include


router = routers.DefaultRouter()
router.register(r'tracks', TrackViewSet)
router.register(r'hosts', HostViewSet)
router.register(r'cves', CVEViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
