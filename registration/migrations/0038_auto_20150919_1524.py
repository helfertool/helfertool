# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0037_auto_20150917_1448'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeSettings',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('badge_design', models.OneToOneField(to='registration.BadgeDesign')),
            ],
        ),
        migrations.RemoveField(
            model_name='event',
            name='badge_design',
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='event',
            field=models.OneToOneField(to='registration.Event'),
        ),
    ]
