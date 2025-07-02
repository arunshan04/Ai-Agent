
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Track, CVE
from .serializers import TrackSerializer, CVESerializer

class TrackListApiView(APIView):
    def get(self, request, *args, **kwargs):
        tracks = Track.objects.all()
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CVEListApiView(APIView):
    # List all CVEs
    def get(self, request, *args, **kwargs):
        '''
        List all the cve items
        '''
        cves = CVE.objects.all()
        serializer = CVESerializer(cves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CVEListApiView(APIView):
    # List all CVEs
    def get(self, request, *args, **kwargs):
        '''
        List all the cve items
        '''
        cves = CVE.objects.all()
        serializer = CVESerializer(cves, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)