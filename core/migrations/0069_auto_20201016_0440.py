# Generated by Django 2.2.4 on 2020-10-16 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0068_auto_20201016_0439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='booster_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='subs_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]