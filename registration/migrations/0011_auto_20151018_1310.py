# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import registration.models.badge


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0010_auto_20151017_1504'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='photo',
            field=models.ImageField(upload_to=registration.models.badge._badge_upload_path, blank=True, verbose_name='Photo', null=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='job',
            field=models.CharField(max_length=200, verbose_name='Other text for job', blank=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='prename',
            field=models.CharField(max_length=200, verbose_name='Other prename', blank=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='primary_job',
            field=models.ForeignKey(help_text='Only necessary if this person has multiple jobs.', to='registration.Job', verbose_name='Primary job', blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='role',
            field=models.CharField(max_length=200, verbose_name='Other text for role', blank=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='shift',
            field=models.CharField(max_length=200, verbose_name='Other text for shift', blank=True),
        ),
        migrations.AlterField(
            model_name='badge',
            name='surname',
            field=models.CharField(max_length=200, verbose_name='Other surname', blank=True),
        ),
    ]
