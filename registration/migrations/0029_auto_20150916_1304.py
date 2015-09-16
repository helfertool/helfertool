# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0028_auto_20150916_1246'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='mail_validation',
            field=models.BooleanField(default=True, verbose_name='Registrations for public shifts must be validated by a link that is sent per mail'),
        ),
        migrations.AddField(
            model_name='helper',
            name='validated',
            field=models.BooleanField(default=False),
        ),
    ]
