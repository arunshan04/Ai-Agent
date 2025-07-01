

from django.contrib import admin
from .models import Track, Host, CVE

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)

from django.urls import path
from django.utils.html import format_html
from django.shortcuts import redirect, render
from django import forms
from django.db import connection
from django.contrib import messages

class PackageUploadForm(forms.Form):
    package_file = forms.FileField(label="Upload package list file")

@admin.register(Host)
class HostAdmin(admin.ModelAdmin):
    list_display = ("name", "os_type", "track", "upload_packages_link")
    list_filter = ("os_type", "track")
    search_fields = ("name",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:host_id>/upload-packages/', self.admin_site.admin_view(self.upload_packages), name='upload-packages'),
        ]
        return custom_urls + urls

    def upload_packages_link(self, obj):
        return format_html(
            '<a href="{}" title="Upload packages"><img src="https://img.icons8.com/material-outlined/24/000000/upload.png" style="vertical-align:middle;"/></a>',
            f"{obj.id}/upload-packages/"
        )
    upload_packages_link.short_description = "Upload Packages"

    def upload_packages(self, request, host_id):
        if request.method == 'POST':
            form = PackageUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data['package_file']
                # Read and process file
                lines = file.read().decode('utf-8').splitlines()
                # Skip header if present
                if lines and (lines[0].lower().startswith('packagename') or ',' in lines[0]):
                    lines = lines[1:]
                rows = []
                for line in lines:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 2:
                        package_name, installed_date = parts[0], parts[1]
                        rows.append((host_id, package_name, installed_date))
                # Insert into raw SQL table
                with connection.cursor() as cursor:
                    cursor.executemany(
                        'INSERT INTO host_packages (host_id, package_name, installed_date) VALUES (?, ?, ?)',
                        rows
                    )

# --- Create local table package_vulnerabilities_mapping if not exists ---
def ensure_package_vulnerabilities_mapping_table():
    table_sql = '''
    CREATE TABLE IF NOT EXISTS package_vulnerabilities_mapping (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        package_name VARCHAR(255) NOT NULL,
        cve_id VARCHAR(64),
        cve_title VARCHAR(255),
        cve_description TEXT,
        score FLOAT,
        impact VARCHAR(64),
        status VARCHAR(64),
        other_fields TEXT,
        updated_ts DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    '''
    with connection.cursor() as cursor:
        cursor.execute(table_sql)


# Ensure table exists at import time
ensure_package_vulnerabilities_mapping_table()

@admin.register(CVE)
class CVEAdmin(admin.ModelAdmin):
    list_display = ("cve_id", "score", "impact")
    search_fields = ("cve_id", "description")
