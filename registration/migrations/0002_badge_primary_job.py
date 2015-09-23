# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='primary_job',
            field=models.ForeignKey(blank=True, null=True, to='registration.Job'),
        ),
    ]
