# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0008_event_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='comment',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
