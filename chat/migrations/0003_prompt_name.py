# Generated by Django 4.2 on 2023-04-29 03:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_rename_character_chat_role_alter_chat_tokens'),
    ]

    operations = [
        migrations.AddField(
            model_name='prompt',
            name='name',
            field=models.CharField(default='PromptName', max_length=128, unique=True),
            preserve_default=False,
        ),
    ]
