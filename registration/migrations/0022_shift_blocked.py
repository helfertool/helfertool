# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0021_job_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='blocked',
            field=models.BooleanField(verbose_name='If the job is publicly visible, the shift is blocked.', default=False),
        ),
    ]
