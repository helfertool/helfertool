# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0023_job_coordinators'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeDesign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('font_color', models.CharField(verbose_name='Color for text', validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$')], help_text='E.g. #00ff00', max_length=7)),
                ('bg_front', models.ImageField(verbose_name='Background image for front', upload_to='')),
                ('bg_back', models.ImageField(verbose_name='Background image for back', upload_to='')),
            ],
        ),
        migrations.AddField(
            model_name='event',
            name='badges',
            field=models.BooleanField(verbose_name='Use badge creation', default=False),
        ),
        migrations.AddField(
            model_name='event',
            name='badge_design',
            field=models.ForeignKey(null=True, to='registration.BadgeDesign', blank=True),
        ),
    ]
