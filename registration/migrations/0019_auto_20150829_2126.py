# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('registration', '0018_auto_20150630_1750'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='job_admins',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shift',
            name='number',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(0)], verbose_name='Number of helpers', default=0),
        ),
    ]
