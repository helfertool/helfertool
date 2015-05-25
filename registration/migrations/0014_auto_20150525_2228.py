# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0013_auto_20150525_1945'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='ask_shirt',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='event',
            name='ask_vegetarian',
            field=models.BooleanField(default=True),
        ),
    ]
