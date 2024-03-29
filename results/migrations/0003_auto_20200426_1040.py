# Generated by Django 2.2.10 on 2020-04-26 10:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0002_auto_20200305_1556"),
    ]

    operations = [
        migrations.AlterField(
            model_name="competition",
            name="event",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="competitions",
                to="results.Event",
            ),
        ),
    ]
