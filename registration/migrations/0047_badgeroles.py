# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0046_auto_20150919_1812'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeRoles',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('permissions', models.ManyToManyField(blank=True, to='registration.BadgePermission')),
            ],
        ),
    ]
