from django.core.management.base import BaseCommand
from django.db import connection
import datetime

class Command(BaseCommand):
    help = 'Populates the package_vulnerabilities_mapping table with sample data.'

    def handle(self, *args, **options):
        self.stdout.write("Checking for existing data...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM package_vulnerabilities_mapping")
            count = cursor.fetchone()[0]
            if count > 0:
                self.stdout.write(self.style.WARNING('Data already exists in package_vulnerabilities_mapping. Aborting.'))
                return

        self.stdout.write("Populating package_vulnerabilities_mapping with sample data...")

        sample_vulns = [
            {
                "package_name": "openssl",
                "cve_id": "CVE-2023-3817",
                "cve_title": "openssl: Excessive time spent checking DH q parameter value",
                "cve_description": "Issue summary: Checking excessively long DH keys or parameters may be very slow.",
                "score": 7.5,
                "impact": "High",
                "status": "Fix Released",
                "other_fields": "Requires attacker to provide malicious keys.",
            },
            {
                "package_name": "requests",
                "cve_id": "CVE-2023-32681",
                "cve_title": "requests: Leaking Proxy-Authorization headers to destination",
                "cve_description": "When making a request to a URL that redirects, Requests can leak the Proxy-Authorization header to the redirected host.",
                "score": 6.1,
                "impact": "Medium",
                "status": "Patch Available",
                "other_fields": "Affects versions before 2.31.0",
            },
            {
                "package_name": "numpy",
                "cve_id": "CVE-2024-21643",
                "cve_title": "numpy: tempfile.mkdtemp is vulnerable to a race condition",
                "cve_description": "The use of `tempfile.mkdtemp` is vulnerable to a race condition. This may allow an attacker to read and write files in the temporary directory.",
                "score": 5.9,
                "impact": "Medium",
                "status": "Investigating",
                "other_fields": "Related to numpy.distutils.",
            },
            {
                "package_name": "django",
                "cve_id": "CVE-2024-24680",
                "cve_title": "django: Potential denial-of-service in `django.utils.text.Truncator`",
                "cve_description": "The `django.utils.text.Truncator`'s `chars()` and `words()` methods were subject to a potential denial-of-service attack on inputs with a large number of certain characters.",
                "score": 7.5,
                "impact": "High",
                "status": "Fix Released",
                "other_fields": "Affects Django main branch and versions 5.0, 4.2, 3.2.",
            }
        ]

        with connection.cursor() as cursor:
            for vuln in sample_vulns:
                cursor.execute(
                    """
                    INSERT INTO package_vulnerabilities_mapping (package_name, cve_id, cve_title, cve_description, score, impact, status, other_fields, updated_ts) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    [vuln[key] for key in vuln] + [datetime.datetime.now()]
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated package_vulnerabilities_mapping with sample data.'))
        self.stdout.write(self.style.NOTICE('To see these vulnerabilities in the "Track View", ensure that hosts are configured with packages like "openssl", "requests", "numpy", or "django".'))