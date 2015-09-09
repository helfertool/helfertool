# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0026_auto_20150905_1350'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='badge_design',
            field=models.ForeignKey(to='registration.BadgeDesign', null=True, blank=True),
        ),
    ]
