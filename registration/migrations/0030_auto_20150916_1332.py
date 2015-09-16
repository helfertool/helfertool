# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0029_auto_20150916_1304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='validated',
            field=models.BooleanField(default=True),
        ),
    ]
