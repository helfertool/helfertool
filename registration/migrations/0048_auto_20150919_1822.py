# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0047_badgeroles'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(verbose_name='Name', max_length=200, null=True)),
                ('name_en', models.CharField(verbose_name='Name', max_length=200, null=True)),
                ('permissions', models.ManyToManyField(to='registration.BadgePermission', blank=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='badgeroles',
            name='permissions',
        ),
        migrations.DeleteModel(
            name='BadgeRoles',
        ),
    ]
