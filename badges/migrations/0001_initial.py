# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import badges.models.badge
import badges.models.design
import badges.models.settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('firstname', models.CharField(max_length=200, blank=True, verbose_name='Other firstname')),
                ('surname', models.CharField(max_length=200, blank=True, verbose_name='Other surname')),
                ('job', models.CharField(max_length=200, blank=True, verbose_name='Other text for job')),
                ('shift', models.CharField(max_length=200, blank=True, verbose_name='Other text for shift')),
                ('role', models.CharField(max_length=200, blank=True, verbose_name='Other text for role')),
                ('photo', models.ImageField(null=True, upload_to=badges.models.badge._badge_upload_path, blank=True, verbose_name='Photo')),
                ('printed', models.BooleanField(default=False, verbose_name='Badge was printed already')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeDefaults',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeDesign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('name_en', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('font_color', models.CharField(default='#000000', validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$')], max_length=7, help_text='E.g. #00ff00', verbose_name='Color for text')),
                ('bg_front', models.ImageField(upload_to=badges.models.design._design_upload_path, verbose_name='Background image for front')),
                ('bg_back', models.ImageField(upload_to=badges.models.design._design_upload_path, verbose_name='Background image for back')),
            ],
        ),
        migrations.CreateModel(
            name='BadgePermission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('name_en', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('latex_name', models.CharField(max_length=200, help_text='This name is used for the LaTeX template, the prefix "perm-" is added.', verbose_name='Name for LaTeX template')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeRole',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('name_en', models.CharField(null=True, max_length=200, verbose_name='Name')),
                ('latex_name', models.CharField(max_length=200, help_text='This name is used for the LaTeX template.', verbose_name='Name for LaTeX template')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeSettings',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('latex_template', models.FileField(null=True, upload_to=badges.models.settings._settings_upload_path, verbose_name='LaTeX template')),
                ('rows', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of rows on one page')),
                ('columns', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of columns on one page')),
                ('barcodes', models.BooleanField(default=False, verbose_name='Print barcodes on badges to avoid duplicates')),
                ('coordinator_title', models.CharField(default='', max_length=200, verbose_name='Role for coordinators')),
                ('helper_title', models.CharField(default='', max_length=200, verbose_name='Role for helpers')),
                ('defaults', models.OneToOneField(to='badges.BadgeDefaults')),
            ],
        ),
    ]
