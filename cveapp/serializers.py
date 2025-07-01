from rest_framework import serializers
from .models import Host, CVE

class HostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Host
        fields = '__all__'

class CVESerializer(serializers.ModelSerializer):
    class Meta:
        model = CVE
        fields = '__all__'


