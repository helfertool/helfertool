# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0017_auto_20151114_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='helper',
            name='firstname',
            field=models.CharField(verbose_name='First name', max_length=200),
        ),
    ]
