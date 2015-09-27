# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_auto_20150928_0007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badge',
            name='job',
            field=models.CharField(blank=True, verbose_name='Job', max_length=200),
        ),
        migrations.AlterField(
            model_name='badge',
            name='role',
            field=models.CharField(blank=True, verbose_name='Role', max_length=200),
        ),
        migrations.AlterField(
            model_name='badge',
            name='shift',
            field=models.CharField(blank=True, verbose_name='Shift', max_length=200),
        ),
        migrations.AlterField(
            model_name='badge',
            name='surname',
            field=models.CharField(blank=True, verbose_name='Surname', max_length=200),
        ),
    ]
