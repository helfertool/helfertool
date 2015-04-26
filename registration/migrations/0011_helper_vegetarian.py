# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0010_helper_timestamp'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='vegetarian',
            field=models.BooleanField(default=False),
        ),
    ]
