# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0045_auto_20150919_1741'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgepermission',
            name='name_de',
            field=models.CharField(verbose_name='Name', null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='badgepermission',
            name='name_en',
            field=models.CharField(verbose_name='Name', null=True, max_length=200),
        ),
    ]
