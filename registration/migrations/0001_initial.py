# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.core.validators
import registration.models.badge
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('prename', models.CharField(verbose_name='Prename', max_length=200)),
                ('surname', models.CharField(verbose_name='Surname', max_length=200)),
                ('job', models.CharField(verbose_name='Job', max_length=200)),
                ('shift', models.CharField(verbose_name='Shift', max_length=200)),
                ('role', models.CharField(verbose_name='Role', max_length=200)),
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
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('name_en', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('font_color', models.CharField(help_text='E.g. #00ff00', verbose_name='Color for text', max_length=7, validators=[django.core.validators.RegexValidator('^#[a-fA-F0-9]{6}$')], default='#000000')),
                ('bg_front', models.ImageField(verbose_name='Background image for front', upload_to=registration.models.badge._design_upload_path)),
                ('bg_back', models.ImageField(verbose_name='Background image for back', upload_to=registration.models.badge._design_upload_path)),
            ],
        ),
        migrations.CreateModel(
            name='BadgePermission',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('name_en', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('latex_name', models.CharField(help_text='This name is used for the LaTeX template, the prefix "perm-" is added.', verbose_name='Name for LaTeX template', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='BadgeRole',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('name_en', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('latex_name', models.CharField(help_text='This name is used for the LaTeX template.', verbose_name='Name for LaTeX template', max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='BadgeSettings',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('latex_template', models.FileField(null=True, verbose_name='LaTeX template', upload_to=registration.models.badge._settings_upload_path)),
                ('rows', models.IntegerField(verbose_name='Number of rows on one page', validators=[django.core.validators.MinValueValidator(1)], default=5)),
                ('columns', models.IntegerField(verbose_name='Number of columns on one page', validators=[django.core.validators.MinValueValidator(1)], default=2)),
                ('defaults', models.OneToOneField(to='registration.BadgeDefaults')),
            ],
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('url_name', models.CharField(unique=True, help_text='May contain the following chars: a-zA-Z0-9.', verbose_name='Name for URL', max_length=200, validators=[django.core.validators.RegexValidator('^[a-zA-Z0-9]+$')])),
                ('name', models.CharField(verbose_name='Event name', max_length=200)),
                ('text', models.TextField(help_text='Displayed as first text of the registration form.', verbose_name='Text before registration', blank=True)),
                ('text_de', models.TextField(help_text='Displayed as first text of the registration form.', null=True, verbose_name='Text before registration', blank=True)),
                ('text_en', models.TextField(help_text='Displayed as first text of the registration form.', null=True, verbose_name='Text before registration', blank=True)),
                ('imprint', models.TextField(help_text='Display at the bottom of the registration form.', verbose_name='Imprint', blank=True)),
                ('imprint_de', models.TextField(help_text='Display at the bottom of the registration form.', null=True, verbose_name='Imprint', blank=True)),
                ('imprint_en', models.TextField(help_text='Display at the bottom of the registration form.', null=True, verbose_name='Imprint', blank=True)),
                ('registered', models.TextField(help_text='Displayed after registration.', verbose_name='Text after registration', blank=True)),
                ('registered_de', models.TextField(help_text='Displayed after registration.', null=True, verbose_name='Text after registration', blank=True)),
                ('registered_en', models.TextField(help_text='Displayed after registration.', null=True, verbose_name='Text after registration', blank=True)),
                ('email', models.EmailField(help_text='Used as sender of e-mails.', verbose_name='E-Mail', max_length=254, default='party@fs.tum.de')),
                ('active', models.BooleanField(verbose_name='Registration possible', default=False)),
                ('ask_shirt', models.BooleanField(verbose_name='Ask for T-shirt size', default=True)),
                ('ask_vegetarian', models.BooleanField(verbose_name='Ask, if helper is vegetarian', default=True)),
                ('show_public_numbers', models.BooleanField(verbose_name='Show number of helpers on registration page', default=True)),
                ('mail_validation', models.BooleanField(verbose_name='Registrations for public shifts must be validated by a link that is sent per mail', default=True)),
                ('badges', models.BooleanField(verbose_name='Use badge creation', default=False)),
                ('admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Helper',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, default=uuid.uuid4)),
                ('prename', models.CharField(verbose_name='Prename', max_length=200)),
                ('surname', models.CharField(verbose_name='Surname', max_length=200)),
                ('email', models.EmailField(verbose_name='E-Mail', max_length=254)),
                ('phone', models.CharField(verbose_name='Mobile phone', max_length=200)),
                ('comment', models.CharField(verbose_name='Comment', max_length=200, blank=True)),
                ('shirt', models.CharField(verbose_name='T-shirt', max_length=20, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')], default='S')),
                ('vegetarian', models.BooleanField(help_text='This helps us estimating the food for our helpers.', verbose_name='Vegetarian', default=False)),
                ('infection_instruction', models.CharField(verbose_name='Instruction for the handling of food', max_length=20, choices=[('No', 'I never got an instruction'), ('Yes', 'I have a valid instruction'), ('Refresh', 'I got a instruction by a doctor, it must be refreshed')], blank=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('validated', models.BooleanField(verbose_name='E-Mail address was confirmed', default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Name', max_length=200)),
                ('name_de', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('name_en', models.CharField(null=True, verbose_name='Name', max_length=200)),
                ('public', models.BooleanField(verbose_name='This job is visible publicly', default=False)),
                ('infection_instruction', models.BooleanField(verbose_name='Instruction for the handling of food necessary', default=False)),
                ('description', models.TextField(verbose_name='Description', blank=True)),
                ('description_de', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('description_en', models.TextField(null=True, verbose_name='Description', blank=True)),
                ('badge_defaults', models.OneToOneField(blank=True, null=True, to='registration.BadgeDefaults')),
                ('coordinators', models.ManyToManyField(to='registration.Helper', blank=True)),
                ('event', models.ForeignKey(to='registration.Event')),
                ('job_admins', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.UUIDField(editable=False, primary_key=True, serialize=False, default=uuid.uuid4)),
                ('usage', models.CharField(verbose_name='Usage', max_length=200, blank=True)),
                ('creator', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('event', models.ForeignKey(to='registration.Event')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('begin', models.DateTimeField(verbose_name='Begin')),
                ('end', models.DateTimeField(verbose_name='End')),
                ('number', models.IntegerField(verbose_name='Number of helpers', validators=[django.core.validators.MinValueValidator(0)], default=0)),
                ('blocked', models.BooleanField(verbose_name='If the job is publicly visible, the shift is blocked.', default=False)),
                ('job', models.ForeignKey(to='registration.Job')),
            ],
            options={
                'ordering': ['job', 'begin', 'end'],
            },
        ),
        migrations.AddField(
            model_name='link',
            name='shifts',
            field=models.ManyToManyField(to='registration.Shift'),
        ),
        migrations.AddField(
            model_name='helper',
            name='shifts',
            field=models.ManyToManyField(to='registration.Shift'),
        ),
        migrations.AddField(
            model_name='badgesettings',
            name='event',
            field=models.OneToOneField(to='registration.Event'),
        ),
        migrations.AddField(
            model_name='badgerole',
            name='badge_settings',
            field=models.ForeignKey(to='registration.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgerole',
            name='permissions',
            field=models.ManyToManyField(to='registration.BadgePermission', blank=True),
        ),
        migrations.AddField(
            model_name='badgepermission',
            name='badge_settings',
            field=models.ForeignKey(to='registration.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgedesign',
            name='badge_settings',
            field=models.ForeignKey(to='registration.BadgeSettings'),
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='design',
            field=models.ForeignKey(verbose_name='Default design', blank=True, related_name='+', null=True, to='registration.BadgeDesign'),
        ),
        migrations.AddField(
            model_name='badgedefaults',
            name='role',
            field=models.ForeignKey(verbose_name='Default role', blank=True, related_name='+', null=True, to='registration.BadgeRole'),
        ),
        migrations.AddField(
            model_name='badge',
            name='helper',
            field=models.OneToOneField(to='registration.Helper'),
        ),
    ]
