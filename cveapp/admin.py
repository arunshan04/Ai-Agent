

from django.contrib import admin
from .models import Track, Host, CVE, HostCVE

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "os_type", "track")
    list_filter = ("os_type", "track")
    search_fields = ("name",)

@admin.register(CVE)
class CVEAdmin(admin.ModelAdmin):
    list_display = ("cve_id", "score", "impact")
    search_fields = ("cve_id", "description")

@admin.register(HostCVE)
class HostCVEAdmin(admin.ModelAdmin):
    list_display = ("host", "cve")
    list_filter = ("host", "cve")
