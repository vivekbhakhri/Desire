# Generated by Django 2.2.4 on 2020-10-17 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0073_auto_20201016_1208'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='brandName',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]