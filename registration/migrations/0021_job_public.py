# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0020_auto_20150829_2203'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='public',
            field=models.BooleanField(default=False, verbose_name='This job is visible publicly'),
        ),
    ]
