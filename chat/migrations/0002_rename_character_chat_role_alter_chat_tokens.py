# Generated by Django 4.2 on 2023-04-14 14:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="chat",
            old_name="character",
            new_name="role",
        ),
        migrations.AlterField(
            model_name="chat",
            name="tokens",
            field=models.IntegerField(default=0),
        ),
    ]
