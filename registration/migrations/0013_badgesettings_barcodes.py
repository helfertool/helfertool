# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0012_auto_20151018_1946'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='barcodes',
            field=models.BooleanField(verbose_name='Print barcodes on badges to avoid duplicates', default=False),
        ),
    ]
