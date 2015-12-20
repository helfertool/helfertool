# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0023_remove_helper_full_age'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='ask_full_age',
            field=models.BooleanField(verbose_name='Helpers have to confirm to be full age', default=True),
        ),
    ]
