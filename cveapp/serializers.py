from rest_framework import serializers
from .models import Host, CVE, HostCVE

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'

class CVESerializer(serializers.ModelSerializer):
    class Meta:
        model = CVE
        fields = '__all__'

class HostCVESerializer(serializers.ModelSerializer):
    host = HostSerializer()
    cve = CVESerializer()
    class Meta:
        model = HostCVE
        fields = '__all__'
