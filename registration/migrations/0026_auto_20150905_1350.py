# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0025_auto_20150905_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgedesign',
            name='bg_back',
            field=models.ImageField(upload_to='/home/hertle/Programmieren/helfertool/helfertool/badgeupload', verbose_name='Background image for back'),
        ),
        migrations.AlterField(
            model_name='badgedesign',
            name='bg_front',
            field=models.ImageField(upload_to='/home/hertle/Programmieren/helfertool/helfertool/badgeupload', verbose_name='Background image for front'),
        ),
    ]
