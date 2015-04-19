# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0003_auto_20150419_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='url_name',
            field=models.CharField(unique=True, default="", max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
