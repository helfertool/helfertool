# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0004_auto_20150928_0007'),
    ]

    operations = [
        migrations.AddField(
            model_name='helper',
            name='event',
            field=models.ForeignKey(default=None, to='registration.Event'),
            preserve_default=False,
        ),
    ]
