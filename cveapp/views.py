from django.db import connection
# API endpoint for CVE summary charts
from rest_framework.views import APIView
from rest_framework.response import Response
class CVESummaryChartsApiView(APIView):
    def get(self, request, *args, **kwargs):
        # CVEs by severity
        with connection.cursor() as cursor:
            cursor.execute('SELECT severity, COUNT(*) FROM cve_summary GROUP BY severity')
            severity_data = dict(cursor.fetchall())
        # CVEs by month (last 7 months)
        with connection.cursor() as cursor:
            cursor.execute('SELECT substr(published_date, 1, 7) as month, COUNT(*) FROM cve_summary GROUP BY month ORDER BY month DESC LIMIT 7')
            month_data = cursor.fetchall()
        # CVEs by CVSS score (rounded)
        with connection.cursor() as cursor:
            cursor.execute('SELECT ROUND(cvss_score), COUNT(*) FROM cve_summary GROUP BY ROUND(cvss_score) ORDER BY ROUND(cvss_score)')
            cvss_data = cursor.fetchall()
        return Response({
            'severity': severity_data,
            'monthly': [{'month': m, 'count': c} for m, c in month_data],
            'cvss': [{'score': s if s is not None else 'Unspecified', 'count': c} for s, c in cvss_data],
        })

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