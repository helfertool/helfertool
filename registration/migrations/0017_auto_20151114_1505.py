# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0016_shift_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='event',
            options={'ordering': ['name', 'url_name']},
        ),
        migrations.RenameField(
            model_name='helper',
            old_name='prename',
            new_name='firstname',
        ),
        migrations.RemoveField(
            model_name='badge',
            name='prename',
        ),
        migrations.AddField(
            model_name='badge',
            name='firstname',
            field=models.CharField(blank=True, max_length=200, verbose_name='Other firstname'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Name (optional)', default=''),
        ),
    ]
