# Generated by Django 2.2.12 on 2020-05-10 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("results", "0003_auto_20200426_1040"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoryforcompetitiontype",
            name="check_record_partial",
            field=models.BooleanField(default=True, verbose_name="Check partial records"),
        ),
    ]
