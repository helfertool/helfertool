# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_auto_20150419_1422'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='imprint',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='text',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(blank=True),
        ),
    ]
