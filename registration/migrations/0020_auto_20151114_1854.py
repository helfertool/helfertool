# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0019_auto_20151114_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='imprint',
            field=django_bleach.models.BleachField(verbose_name='Imprint', blank=True, help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint_de',
            field=django_bleach.models.BleachField(null=True, verbose_name='Imprint', blank=True, help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='imprint_en',
            field=django_bleach.models.BleachField(null=True, verbose_name='Imprint', blank=True, help_text='Display at the bottom of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered',
            field=django_bleach.models.BleachField(verbose_name='Text after registration', blank=True, help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered_de',
            field=django_bleach.models.BleachField(null=True, verbose_name='Text after registration', blank=True, help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='registered_en',
            field=django_bleach.models.BleachField(null=True, verbose_name='Text after registration', blank=True, help_text='Displayed after registration.'),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=django_bleach.models.BleachField(verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_de',
            field=django_bleach.models.BleachField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_en',
            field=django_bleach.models.BleachField(null=True, verbose_name='Description', blank=True),
        ),
    ]
