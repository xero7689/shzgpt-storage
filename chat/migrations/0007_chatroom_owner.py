# Generated by Django 4.2 on 2023-06-16 12:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0006_chatuser_created_at_chatuser_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='chat.chatuser'),
            preserve_default=False,
        ),
    ]
