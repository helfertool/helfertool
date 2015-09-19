# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0044_auto_20150919_1644'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgesettings',
            name='permissions',
        ),
        migrations.AddField(
            model_name='badgepermission',
            name='badge_settings',
            field=models.ForeignKey(default=None, to='registration.BadgeSettings'),
            preserve_default=False,
        ),
    ]
