# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0022_shift_blocked'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='coordinators',
            field=models.ManyToManyField(to='registration.Helper', blank=True),
        ),
    ]
