# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0035_auto_20150916_1923'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='shift',
            options={'ordering': ['begin', 'end']},
        ),
        migrations.AddField(
            model_name='link',
            name='usage',
            field=models.CharField(max_length=200, blank=True, verbose_name='Usage'),
        ),
    ]
