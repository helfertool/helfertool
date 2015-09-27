# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0002_badge_primary_job'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='prename',
            field=models.CharField(blank=True, verbose_name='Prename', max_length=200),
        ),
    ]
