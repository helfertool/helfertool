# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0008_auto_20151003_1323'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='max_overlapping',
            field=models.IntegerField(null=True, verbose_name='Maximal overlapping of shifts', blank=True, help_text='If two shifts overlap this value in minutes or more it is not possible to register for both shifts. Leave empty to disable this check.'),
        ),
    ]
