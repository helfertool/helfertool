# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0020_auto_20151114_1854'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='ask_full_age',
            field=models.BooleanField(default=True, verbose_name='The helper has to confirm to be full age'),
        ),
        migrations.AddField(
            model_name='helper',
            name='full_age',
            field=models.NullBooleanField(default=None, verbose_name='Helper is full age'),
        ),
    ]
