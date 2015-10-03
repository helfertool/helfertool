# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0005_helper_event'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='logo',
            field=models.ImageField(blank=True, upload_to='logos', null=True, verbose_name='Logo'),
        ),
    ]
