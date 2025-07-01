from rest_framework import routers
from cveapp.views import HostViewSet, CVEViewSet, TrackViewSet, package_vulnerabilities_list
from django.urls import path, include


router = routers.DefaultRouter()
router.register(r'tracks', TrackViewSet)
router.register(r'hosts', HostViewSet)
router.register(r'cves', CVEViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/package-vulnerabilities/', package_vulnerabilities_list, name='package-vulnerabilities-list'),
]
