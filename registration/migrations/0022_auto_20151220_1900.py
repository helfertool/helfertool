# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0021_auto_20151220_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='full_age',
            field=models.BooleanField(verbose_name='Helper is full age', default=True),
        ),
    ]
