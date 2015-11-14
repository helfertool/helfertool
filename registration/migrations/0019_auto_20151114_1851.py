# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_bleach.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0018_auto_20151114_1508'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='text',
            field=django_bleach.models.BleachField(blank=True, verbose_name='Text before registration', help_text='Displayed as first text of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='text_de',
            field=django_bleach.models.BleachField(null=True, blank=True, verbose_name='Text before registration', help_text='Displayed as first text of the registration form.'),
        ),
        migrations.AlterField(
            model_name='event',
            name='text_en',
            field=django_bleach.models.BleachField(null=True, blank=True, verbose_name='Text before registration', help_text='Displayed as first text of the registration form.'),
        ),
    ]
