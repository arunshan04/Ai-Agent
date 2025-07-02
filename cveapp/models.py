from django.db import models

class Track(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class Host(models.Model):
    name = models.CharField(max_length=255, unique=True)
    os_type = models.CharField(max_length=50)
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class CVE(models.Model):
    cve_id = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    score = models.FloatField(null=True, blank=True)
    impact = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.cve_id