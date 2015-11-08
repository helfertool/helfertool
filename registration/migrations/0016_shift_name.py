# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0015_auto_20151101_1306'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='name',
            field=models.CharField(default='', max_length=200, blank=True, verbose_name='Name'),
        ),
    ]
