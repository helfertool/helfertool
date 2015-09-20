# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0050_auto_20150919_2107'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='badge_role',
            field=models.ForeignKey(verbose_name='Default role for this job', null=True, blank=True, to='registration.BadgeRole', related_name='+'),
        ),
        migrations.AlterField(
            model_name='badgesettings',
            name='coordinator_role',
            field=models.ForeignKey(verbose_name='Default role for coordinators', null=True, blank=True, to='registration.BadgeRole', related_name='+'),
        ),
        migrations.AlterField(
            model_name='badgesettings',
            name='role',
            field=models.ForeignKey(verbose_name='Default role for all helpers', null=True, blank=True, to='registration.BadgeRole', related_name='+'),
        ),
    ]
