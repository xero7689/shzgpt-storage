# Generated by Django 4.2 on 2023-06-16 12:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0005_alter_chatroom_last_used_time_chatuser'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatuser',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Topic Created Date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='chatuser',
            name='name',
            field=models.CharField(default='Peter', max_length=64),
            preserve_default=False,
        ),
    ]