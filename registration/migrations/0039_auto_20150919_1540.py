# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0038_auto_20150919_1524'),
    ]

    operations = [
        migrations.RenameField(
            model_name='badgesettings',
            old_name='badge_design',
            new_name='design',
        ),
    ]
