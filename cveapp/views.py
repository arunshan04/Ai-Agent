
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Host, CVE, Track
from .serializers import HostSerializer, CVESerializer
from .track_serializers import TrackSerializer
from rest_framework import viewsets
from django.db import connection
from rest_framework.decorators import api_view

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class TrackViewSet(viewsets.ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class CVEViewSet(viewsets.ModelViewSet):
    queryset = CVE.objects.all()
    serializer_class = CVESerializer

@api_view(['GET'])
def package_vulnerabilities_list(request):
    """
    List all package vulnerabilities from the raw SQL table.
    """
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT package_name, cve_id, cve_title, cve_description, score, 
                   impact, status, other_fields, updated_ts 
            FROM package_vulnerabilities_mapping
        """)
        data = dictfetchall(cursor)
    return Response(data)
