# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0030_auto_20150916_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='validated',
            field=models.BooleanField(default=True, verbose_name='E-Mail address was confirmed'),
        ),
    ]
