# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0014_badge_printed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='primary_job',
            field=models.ForeignKey(help_text='Only necessary if this person has multiple jobs.', null=True, blank=True, to='registration.Job', verbose_name='Primary job', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
