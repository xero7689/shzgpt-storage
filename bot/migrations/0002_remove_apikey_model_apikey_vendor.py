# Generated by Django 4.2.15 on 2024-09-16 14:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("bot", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="apikey",
            name="model",
        ),
        migrations.AddField(
            model_name="apikey",
            name="vendor",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="bot.aivendor",
            ),
        ),
    ]