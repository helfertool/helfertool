# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0043_auto_20150919_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgePermission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('latex_name', models.CharField(help_text='This name is used for the LaTeX template, the prefix "perm_" is added.', max_length=200, verbose_name='Name for LaTeX template')),
            ],
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='permissions',
            field=models.ManyToManyField(blank=True, to='registration.BadgePermission'),
        ),
    ]
