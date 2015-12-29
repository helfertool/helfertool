# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('badges', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='helper',
            field=models.OneToOneField(to='registration.Helper'),
        ),
        migrations.AlterField(
            model_name='badge',
            name='primary_job',
            field=models.ForeignKey(to='registration.Job', help_text='Only necessary if this person has multiple jobs.', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Primary job', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='badgesettings',
            name='event',
            field=models.OneToOneField(to='registration.Event'),
        ),
    ]
