# Generated by Django 2.2.11 on 2020-03-14 14:38

from django.db import migrations
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('prerequisites', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='prerequisite',
            name='description',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Description'),
        ),
    ]
