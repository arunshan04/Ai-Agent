
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Host, CVE, HostCVE
from .serializers import HostSerializer, CVESerializer, HostCVESerializer

class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer

class CVEViewSet(viewsets.ModelViewSet):
    queryset = CVE.objects.all()
    serializer_class = CVESerializer

class HostCVEViewSet(viewsets.ModelViewSet):
    queryset = HostCVE.objects.all()
    serializer_class = HostCVESerializer

    @action(detail=False, methods=['get'])
    def by_host(self, request):
        host_id = request.query_params.get('host_id')
        if not host_id:
            return Response({'error': 'host_id required'}, status=400)
        host_cves = HostCVE.objects.filter(host_id=host_id)
        serializer = self.get_serializer(host_cves, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_os(self, request):
        os_type = request.query_params.get('os_type')
        if not os_type:
            return Response({'error': 'os_type required'}, status=400)
        hosts = Host.objects.filter(os_type=os_type)
        host_ids = hosts.values_list('id', flat=True)
        host_cves = HostCVE.objects.filter(host_id__in=host_ids)
        serializer = self.get_serializer(host_cves, many=True)
        return Response(serializer.data)
