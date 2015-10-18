# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0011_auto_20151018_1310'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='coordinator_title',
            field=models.CharField(verbose_name='Role for coordinators', max_length=200, default=''),
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='helper_title',
            field=models.CharField(verbose_name='Role for helpers', max_length=200, default=''),
        ),
    ]
