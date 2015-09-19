# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0039_auto_20150919_1540'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgesettings',
            name='event',
            field=models.OneToOneField(to='registration.Event', related_name='badge_settings'),
        ),
    ]
