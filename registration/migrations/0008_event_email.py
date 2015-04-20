# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0007_auto_20150420_0954'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='email',
            field=models.EmailField(max_length=254, default='party@fs.tum.de'),
        ),
    ]
