# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_auto_20150419_1916'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='registered',
            field=models.TextField(blank=True),
        ),
    ]
