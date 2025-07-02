from django.apps import AppConfig


class CveappConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "cveapp"

    def ready(self):
        """Ensure the custom SQL table exists when the app is ready."""
        from .admin import ensure_package_vulnerabilities_mapping_table
        ensure_package_vulnerabilities_mapping_table()