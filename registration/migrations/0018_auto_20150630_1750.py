# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0017_auto_20150606_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='admins',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='helper',
            name='comment',
            field=models.CharField(verbose_name='Comment', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='helper',
            name='email',
            field=models.EmailField(verbose_name='E-Mail', max_length=254),
        ),
        migrations.AlterField(
            model_name='helper',
            name='infection_instruction',
            field=models.CharField(choices=[('No', 'I never got an instruction'), ('Yes', 'I have a valid instruction'), ('Refresh', 'I got a instruction by a doctor, it must be refreshed')], verbose_name='Instruction for the handling of food', max_length=20, blank=True),
        ),
        migrations.AlterField(
            model_name='helper',
            name='phone',
            field=models.CharField(verbose_name='Mobile phone', max_length=200),
        ),
        migrations.AlterField(
            model_name='helper',
            name='prename',
            field=models.CharField(verbose_name='Prename', max_length=200),
        ),
        migrations.AlterField(
            model_name='helper',
            name='shirt',
            field=models.CharField(default='S', verbose_name='T-shirt', max_length=20, choices=[('S', 'S'), ('M', 'M'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'), ('S_GIRLY', 'S (girly)'), ('M_GIRLY', 'M (girly)'), ('L_GIRLY', 'L (girly)'), ('XL_GIRLY', 'XL (girly)')]),
        ),
        migrations.AlterField(
            model_name='helper',
            name='surname',
            field=models.CharField(verbose_name='Surname', max_length=200),
        ),
        migrations.AlterField(
            model_name='helper',
            name='vegetarian',
            field=models.BooleanField(help_text='This helps us estimating the food for our helpers.', verbose_name='Vegetarian', default=False),
        ),
        migrations.AlterField(
            model_name='job',
            name='description',
            field=models.TextField(verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_de',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='description_en',
            field=models.TextField(null=True, verbose_name='Description', blank=True),
        ),
        migrations.AlterField(
            model_name='job',
            name='infection_instruction',
            field=models.BooleanField(verbose_name='Instruction for the handling of food necessary', default=False),
        ),
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.CharField(verbose_name='Name', max_length=200),
        ),
        migrations.AlterField(
            model_name='job',
            name='name_de',
            field=models.CharField(verbose_name='Name', null=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='job',
            name='name_en',
            field=models.CharField(verbose_name='Name', null=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='shift',
            name='begin',
            field=models.DateTimeField(verbose_name='Begin'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='end',
            field=models.DateTimeField(verbose_name='End'),
        ),
        migrations.AlterField(
            model_name='shift',
            name='number',
            field=models.IntegerField(verbose_name='Number of helpers', default=0),
        ),
    ]
