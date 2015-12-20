# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0022_auto_20151220_1900'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='helper',
            name='full_age',
        ),
    ]
