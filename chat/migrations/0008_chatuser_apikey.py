# Generated by Django 4.2 on 2023-06-16 12:55

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0007_chatroom_owner"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatuser",
            name="apiKey",
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
