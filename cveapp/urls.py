from rest_framework import routers
from cveapp.views import HostViewSet, CVEViewSet, HostCVEViewSet
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'hosts', HostViewSet)
router.register(r'cves', CVEViewSet)
router.register(r'hostcves', HostCVEViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
