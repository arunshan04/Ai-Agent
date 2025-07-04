# Generated by Django 5.2.3 on 2025-06-30 06:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CVE",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("cve_id", models.CharField(max_length=30, unique=True)),
                ("description", models.TextField()),
                ("score", models.FloatField()),
                ("impact", models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name="Host",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=100)),
                (
                    "os_type",
                    models.CharField(
                        choices=[("windows", "Windows"), ("linux", "Linux")],
                        max_length=10,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="HostCVE",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "cve",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cveapp.cve"
                    ),
                ),
                (
                    "host",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="cveapp.host"
                    ),
                ),
            ],
        ),
    ]
