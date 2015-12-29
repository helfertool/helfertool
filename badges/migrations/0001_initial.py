# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import badges.models.badges
import django.core.validators
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0025_auto_20151229_1504'),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('firstname', models.CharField(blank=True, max_length=200, verbose_name='Other firstname')),
                ('surname', models.CharField(blank=True, max_length=200, verbose_name='Other surname')),
                ('job', models.CharField(blank=True, max_length=200, verbose_name='Other text for job')),
                ('shift', models.CharField(blank=True, max_length=200, verbose_name='Other text for shift')),
                ('role', models.CharField(blank=True, max_length=200, verbose_name='Other text for role')),
                ('photo', models.ImageField(blank=True, upload_to=badges.models.badges._badge_upload_path, null=True, verbose_name='Photo')),
                ('printed', models.BooleanField(default=False, verbose_name='Badge was printed already')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeDefaults',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeDesign',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('font_color', models.CharField(default='#000000', help_text='E.g. #00ff00', max_length=7, validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$')], verbose_name='Color for text')),
                ('bg_front', models.ImageField(upload_to=badges.models.badges._design_upload_path, verbose_name='Background image for front')),
                ('bg_back', models.ImageField(upload_to=badges.models.badges._design_upload_path, verbose_name='Background image for back')),
            ],
        ),
        migrations.CreateModel(
            name='BadgePermission',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('latex_name', models.CharField(help_text='This name is used for the LaTeX template, the prefix "perm-" is added.', max_length=200, verbose_name='Name for LaTeX template')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeRole',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name')),
                ('name_de', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('name_en', models.CharField(max_length=200, null=True, verbose_name='Name')),
                ('latex_name', models.CharField(help_text='This name is used for the LaTeX template.', max_length=200, verbose_name='Name for LaTeX template')),
            ],
        ),
        migrations.CreateModel(
            name='BadgeSettings',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('latex_template', models.FileField(upload_to=badges.models.badges._settings_upload_path, null=True, verbose_name='LaTeX template')),
                ('rows', models.IntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of rows on one page')),
                ('columns', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1)], verbose_name='Number of columns on one page')),
                ('barcodes', models.BooleanField(default=False, verbose_name='Print barcodes on badges to avoid duplicates')),
                ('coordinator_title', models.CharField(default='', max_length=200, verbose_name='Role for coordinators')),
                ('helper_title', models.CharField(default='', max_length=200, verbose_name='Role for helpers')),
                ('defaults', models.OneToOneField(to='badges.BadgeDefaults')),
                ('event', models.OneToOneField(to='registration.Event', related_name='event')),
            ],
        ),
        migrations.AddField(
            model_name='badgerole',
            name='badge_settings',
            field=models.ForeignKey(to='badges.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgerole',
            name='permissions',
            field=models.ManyToManyField(to='badges.BadgePermission', blank=True),
        ),
        migrations.AddField(
            model_name='badgepermission',
            name='badge_settings',
            field=models.ForeignKey(to='badges.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgedesign',
            name='badge_settings',
            field=models.ForeignKey(to='badges.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='design',
            field=models.ForeignKey(null=True, verbose_name='Default design', related_name='+', blank=True, to='badges.BadgeDesign'),
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='role',
            field=models.ForeignKey(null=True, verbose_name='Default role', related_name='+', blank=True, to='badges.BadgeRole'),
        ),
        migrations.AddField(
            model_name='badge',
            name='custom_design',
            field=models.ForeignKey(null=True, verbose_name='Design', related_name='+', blank=True, to='badges.BadgeDesign'),
        ),
        migrations.AddField(
            model_name='badge',
            name='custom_role',
            field=models.ForeignKey(null=True, verbose_name='Role', related_name='+', blank=True, to='badges.BadgeRole'),
        ),
        migrations.AddField(
            model_name='badge',
            name='helper',
            field=models.OneToOneField(to='registration.Helper', related_name='helper'),
        ),
        migrations.AddField(
            model_name='badge',
            name='primary_job',
            field=models.ForeignKey(help_text='Only necessary if this person has multiple jobs.', null=True, verbose_name='Primary job', related_name='primary_job', blank=True, on_delete=django.db.models.deletion.SET_NULL, to='registration.Job'),
        ),
    ]
