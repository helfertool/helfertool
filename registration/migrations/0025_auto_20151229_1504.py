# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0024_auto_20151220_1920'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badgedesign',
            name='name_de',
        ),
        migrations.RemoveField(
            model_name='badgedesign',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='badgepermission',
            name='name_de',
        ),
        migrations.RemoveField(
            model_name='badgepermission',
            name='name_en',
        ),
        migrations.RemoveField(
            model_name='badgerole',
            name='name_de',
        ),
        migrations.RemoveField(
            model_name='badgerole',
            name='name_en',
        ),
    ]
