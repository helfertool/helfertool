# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import registration.models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0027_job_badge_design'),
    ]

    operations = [
        migrations.AlterField(
            model_name='badgedesign',
            name='bg_back',
            field=models.ImageField(upload_to=registration.models.BadgeDesign.upload_path, verbose_name='Background image for back'),
        ),
        migrations.AlterField(
            model_name='badgedesign',
            name='bg_front',
            field=models.ImageField(upload_to=registration.models.BadgeDesign.upload_path, verbose_name='Background image for front'),
        ),
        migrations.AlterField(
            model_name='event',
            name='badge_design',
            field=models.OneToOneField(blank=True, to='registration.BadgeDesign', null=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='badge_design',
            field=models.OneToOneField(blank=True, to='registration.BadgeDesign', null=True),
        ),
    ]
