# Generated by Django 4.2 on 2023-06-19 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0008_chatuser_apikey"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="chatuser",
            name="apiKey",
        ),
        migrations.CreateModel(
            name="APIKey",
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
                ("key", models.CharField(max_length=256)),
                ("desc", models.CharField(blank=True, max_length=256)),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Topic Created Date"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="chat.chatuser"
                    ),
                ),
            ],
        ),
    ]
