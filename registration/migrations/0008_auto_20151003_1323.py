# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_event_max_overlapping'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='max_overlapping',
            field=models.IntegerField(blank=True, null=True, verbose_name='Maximal overlapping of shifts so that registrationfor both shifts is possible'),
        ),
    ]
