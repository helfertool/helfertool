# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0006_event_logo'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='max_overlapping',
            field=models.IntegerField(null=True, verbose_name='Maximal overlapping of shifts so that registrationfor both shifts is possible'),
        ),
    ]
