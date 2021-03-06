# Generated by Django 2.2.4 on 2020-10-14 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0064_auto_20201014_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='booster_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='subs_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='days_valid',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='entries_remaining',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
