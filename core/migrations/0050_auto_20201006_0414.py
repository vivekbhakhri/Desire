# Generated by Django 2.2 on 2020-10-06 04:14

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0049_auto_20201005_1532'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Customer',
            new_name='Profile',
        ),
    ]
