# Generated by Django 4.2.15 on 2024-09-15 23:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="Chat",
            new_name="Message",
        ),
    ]
