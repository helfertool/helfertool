# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0032_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='event',
            field=models.ForeignKey(default=None, to='registration.Event'),
            preserve_default=False,
        ),
    ]
