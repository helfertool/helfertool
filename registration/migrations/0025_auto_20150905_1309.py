# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0024_auto_20150905_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgedesign',
            name='font_color',
            field=models.CharField(validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$')], help_text='E.g. #00ff00', verbose_name='Color for text', max_length=7, default='#000000'),
        ),
    ]
