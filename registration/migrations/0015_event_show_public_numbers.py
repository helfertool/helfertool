# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0014_auto_20150525_2228'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='show_public_numbers',
            field=models.BooleanField(default=True),
        ),
    ]
