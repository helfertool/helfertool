# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0051_auto_20150919_2158'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('prename', models.CharField(max_length=200, verbose_name='Prename')),
                ('surname', models.CharField(max_length=200, verbose_name='Surname')),
                ('job', models.CharField(max_length=200, verbose_name='Job')),
                ('shift', models.CharField(max_length=200, verbose_name='Shift')),
                ('role', models.CharField(max_length=200, verbose_name='Role')),
                ('helper', models.OneToOneField(to='registration.Helper')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeDefaults',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='badgesettings',
            name='coordinator_role',
        ),
        migrations.RemoveField(
            model_name='badgesettings',
            name='design',
        ),
        migrations.RemoveField(
            model_name='badgesettings',
            name='role',
        ),
        migrations.RemoveField(
            model_name='job',
            name='badge_design',
        ),
        migrations.RemoveField(
            model_name='job',
            name='badge_role',
        ),
        migrations.AddField(
            model_name='badgedesign',
            name='badge_settings',
            field=models.ForeignKey(default=None, to='registration.BadgeSettings'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='design',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Default design', to='registration.BadgeDesign', related_name='+'),
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='role',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Default role', to='registration.BadgeRole', related_name='+'),
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='defaults',
            field=models.OneToOneField(default=None, to='registration.BadgeDefaults'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='badge_defaults',
            field=models.OneToOneField(null=True, blank=True, to='registration.BadgeDefaults'),
        ),
    ]
