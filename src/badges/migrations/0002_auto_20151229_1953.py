# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("badges", "0001_initial"),
        ("registration", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="badgesettings",
            name="event",
            field=models.OneToOneField(to="registration.Event", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="badgerole",
            name="badge_settings",
            field=models.ForeignKey(to="badges.BadgeSettings", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="badgerole",
            name="permissions",
            field=models.ManyToManyField(blank=True, to="badges.BadgePermission"),
        ),
        migrations.AddField(
            model_name="badgepermission",
            name="badge_settings",
            field=models.ForeignKey(to="badges.BadgeSettings", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="badgedesign",
            name="badge_settings",
            field=models.ForeignKey(to="badges.BadgeSettings", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="badgedefaults",
            name="design",
            field=models.ForeignKey(
                related_name="+",
                null=True,
                to="badges.BadgeDesign",
                verbose_name="Default design",
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="badgedefaults",
            name="role",
            field=models.ForeignKey(
                related_name="+",
                null=True,
                to="badges.BadgeRole",
                verbose_name="Default role",
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="badge",
            name="custom_design",
            field=models.ForeignKey(
                related_name="+",
                null=True,
                to="badges.BadgeDesign",
                verbose_name="Design",
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="badge",
            name="custom_role",
            field=models.ForeignKey(
                related_name="+",
                null=True,
                to="badges.BadgeRole",
                verbose_name="Role",
                blank=True,
                on_delete=models.CASCADE,
            ),
        ),
        migrations.AddField(
            model_name="badge",
            name="helper",
            field=models.OneToOneField(to="registration.Helper", on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name="badge",
            name="primary_job",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                help_text="Only necessary if this person has multiple jobs.",
                verbose_name="Primary job",
                blank=True,
                to="registration.Job",
            ),
        ),
    ]
