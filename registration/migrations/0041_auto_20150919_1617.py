# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import registration.models.badge


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0040_auto_20150919_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgesettings',
            name='latex_template',
            field=models.FileField(verbose_name='LaTeX template', null=True, blank=True, upload_to=registration.models.badge.BadgeSettings.upload_path),
        ),
        migrations.AlterField(
            model_name='badgesettings',
            name='event',
            field=models.OneToOneField(to='registration.Event'),
        ),
    ]
