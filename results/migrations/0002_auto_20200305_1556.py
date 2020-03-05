# Generated by Django 2.2.10 on 2020-03-05 15:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('results', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='athleteinformation',
            name='public',
        ),
        migrations.AddField(
            model_name='athlete',
            name='no_auto_update',
            field=models.BooleanField(default=False, verbose_name='No automatic updates'),
        ),
        migrations.AddField(
            model_name='athleteinformation',
            name='modification_time',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Suomisport update timestamp'),
        ),
        migrations.AddField(
            model_name='athleteinformation',
            name='visibility',
            field=models.CharField(choices=[('P', 'Public'), ('A', 'Authenticated users'), ('S', 'Staff users'), ('U', 'Superuser only')], default='P', max_length=1, verbose_name='Visibility'),
        ),
        migrations.AddField(
            model_name='organization',
            name='historical',
            field=models.BooleanField(default=False, verbose_name='Historical'),
        ),
        migrations.AddField(
            model_name='organization',
            name='sport_id',
            field=models.CharField(blank=True, max_length=15, null=True, unique=True, verbose_name='Sport ID'),
        ),
    ]
