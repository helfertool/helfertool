# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import registration.models.badge


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0042_auto_20150919_1626'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgesettings',
            name='latex_template',
            field=models.FileField(upload_to=registration.models.badge.BadgeSettings.upload_path, null=True, verbose_name='LaTeX template'),
        ),
    ]
