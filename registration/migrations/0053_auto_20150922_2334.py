# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0052_auto_20150922_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='badgerole',
            name='latex_name',
            field=models.CharField(help_text='This name is used for the LaTeX template.', default='', verbose_name='Name for LaTeX template', max_length=200),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='badgepermission',
            name='latex_name',
            field=models.CharField(help_text='This name is used for the LaTeX template, the prefix "perm-" is added.', verbose_name='Name for LaTeX template', max_length=200),
        ),
    ]
