# Generated by Django 4.1.2 on 2022-10-15 17:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("badges", "0022_auto_20211106_1716"),
    ]

    operations = [
        migrations.AlterField(
            model_name="specialbadges",
            name="badges",
            field=models.ManyToManyField(blank=True, related_name="+", to="badges.badge"),
        ),
    ]
