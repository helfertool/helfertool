# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0009_auto_20150420_1712'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2015, 4, 20, 22, 17, 21, 810882, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
