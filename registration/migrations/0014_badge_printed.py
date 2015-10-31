# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0013_badgesettings_barcodes'),
    ]

    operations = [
        migrations.AddField(
            model_name='badge',
            name='printed',
            field=models.BooleanField(default=False, verbose_name='Badge was printed already'),
        ),
    ]
