# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0041_auto_20150919_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='columns',
            field=models.IntegerField(verbose_name='Number of columns on one page', default=2, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='rows',
            field=models.IntegerField(verbose_name='Number of rows on one page', default=5, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
