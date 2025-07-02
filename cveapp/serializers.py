from rest_framework import serializers
from .models import CVE, Track
class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['id', 'name', 'description']

class CVESerializer(serializers.ModelSerializer):
    class Meta:
        model = CVE
        fields = ['id', 'cve_id', 'score', 'impact', 'description']