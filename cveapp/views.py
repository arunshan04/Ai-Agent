
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Host, CVE, Track
from .serializers import HostSerializer, CVESerializer
from .track_serializers import TrackSerializer
from rest_framework import viewsets
class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class CVEViewSet(viewsets.ModelViewSet):
    queryset = CVE.objects.all()
    serializer_class = CVESerializer


