# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0048_auto_20150919_1822'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgerole',
            name='badge_settings',
            field=models.ForeignKey(to='registration.BadgeSettings', default=None),
            preserve_default=False,
        ),
    ]
