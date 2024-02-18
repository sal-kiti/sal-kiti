# Generated by Django 2.2.12 on 2020-07-01 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0005_competition_calendar"),
    ]

    operations = [
        migrations.AddField(
            model_name="resultpartial",
            name="code",
            field=models.CharField(blank=True, max_length=3, verbose_name="Code"),
        ),
        migrations.AlterField(
            model_name="resultpartial",
            name="value",
            field=models.DecimalField(blank=True, decimal_places=1, max_digits=10, null=True, verbose_name="Value"),
        ),
    ]
