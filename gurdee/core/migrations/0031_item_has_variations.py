# Generated by Django 2.2.4 on 2020-08-12 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0030_auto_20200812_1039'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='has_variations',
            field=models.BooleanField(default=True),
        ),
    ]
