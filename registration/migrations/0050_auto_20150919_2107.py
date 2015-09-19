# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0049_badgerole_badge_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='coordinator_role',
            field=models.ForeignKey(null=True, blank=True, related_name='+', to='registration.BadgeRole'),
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='role',
            field=models.ForeignKey(null=True, blank=True, related_name='+', to='registration.BadgeRole'),
        ),
    ]
