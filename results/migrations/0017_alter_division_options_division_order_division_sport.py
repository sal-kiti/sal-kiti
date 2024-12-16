# Generated by Django 4.2.15 on 2024-09-01 09:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0016_eventcontact_athlete"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="division",
            options={
                "ordering": ["sport", "order", "name"],
                "verbose_name": "Division",
                "verbose_name_plural": "Division",
            },
        ),
        migrations.AddField(
            model_name="division",
            name="order",
            field=models.SmallIntegerField(default=0, verbose_name="Order"),
        ),
        migrations.AddField(
            model_name="division",
            name="sport",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="results.sport"
            ),
        ),
    ]