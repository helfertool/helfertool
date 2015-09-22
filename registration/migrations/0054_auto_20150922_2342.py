# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0053_auto_20150922_2334'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgedesign',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=200, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='badgedesign',
            name='name_de',
            field=models.CharField(verbose_name='Name', max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='badgedesign',
            name='name_en',
            field=models.CharField(verbose_name='Name', max_length=200, null=True),
        ),
    ]
