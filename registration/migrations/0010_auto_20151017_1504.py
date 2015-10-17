# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0009_auto_20151003_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='custom_design',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Design', to='registration.BadgeDesign', related_name='+'),
        ),
        migrations.AddField(
            model_name='badge',
            name='custom_role',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Role', to='registration.BadgeRole', related_name='+'),
        ),
        migrations.AlterField(
            model_name='event',
            name='max_overlapping',
            field=models.IntegerField(help_text='If two shifts overlap more than this value in minutes it is not possible to register for both shifts. Leave empty to disable this check.', null=True, blank=True, verbose_name='Maximal overlapping of shifts'),
        ),
    ]
