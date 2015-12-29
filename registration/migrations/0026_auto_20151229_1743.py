# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0025_auto_20151229_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='badge',
            name='custom_design',
        ),
        migrations.RemoveField(
            model_name='badge',
            name='custom_role',
        ),
        migrations.RemoveField(
            model_name='badge',
            name='helper',
        ),
        migrations.RemoveField(
            model_name='badge',
            name='primary_job',
        ),
        migrations.RemoveField(
            model_name='badgedefaults',
            name='design',
        ),
        migrations.RemoveField(
            model_name='badgedefaults',
            name='role',
        ),
        migrations.RemoveField(
            model_name='badgedesign',
            name='badge_settings',
        ),
        migrations.RemoveField(
            model_name='badgepermission',
            name='badge_settings',
        ),
        migrations.RemoveField(
            model_name='badgerole',
            name='badge_settings',
        ),
        migrations.RemoveField(
            model_name='badgerole',
            name='permissions',
        ),
        migrations.RemoveField(
            model_name='badgesettings',
            name='defaults',
        ),
        migrations.RemoveField(
            model_name='badgesettings',
            name='event',
        ),
        migrations.AlterField(
            model_name='job',
            name='badge_defaults',
            field=models.OneToOneField(to='badges.BadgeDefaults', null=True, blank=True),
        ),
        migrations.DeleteModel(
            name='Badge',
        ),
        migrations.DeleteModel(
            name='BadgeDefaults',
        ),
        migrations.DeleteModel(
            name='BadgeDesign',
        ),
        migrations.DeleteModel(
            name='BadgePermission',
        ),
        migrations.DeleteModel(
            name='BadgeRole',
        ),
        migrations.DeleteModel(
            name='BadgeSettings',
        ),
    ]
