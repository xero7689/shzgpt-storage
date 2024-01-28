# Generated by Django 4.2 on 2023-06-20 04:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("chat", "0010_aivendor_aimodel_apikey_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="prompttopic",
            name="owner",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="chat.chatuser",
            ),
            preserve_default=False,
        ),
    ]
