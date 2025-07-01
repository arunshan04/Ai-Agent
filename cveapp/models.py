
from django.db import models


class Track(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Host(models.Model):
    OS_CHOICES = [
        ("windows", "Windows"),
        ("linux", "Linux"),
    ]
    name = models.CharField(max_length=100)
    os_type = models.CharField(max_length=10, choices=OS_CHOICES)
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="hosts", null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.os_type})"

class CVE(models.Model):
    cve_id = models.CharField(max_length=30, unique=True)
    description = models.TextField()
    score = models.FloatField()
    impact = models.CharField(max_length=200)

    def __str__(self):
        return self.cve_id


