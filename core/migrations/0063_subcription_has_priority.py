# Generated by Django 2.2.4 on 2020-10-14 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0062_auto_20201014_1837'),
    ]

    operations = [
        migrations.AddField(
            model_name='subcription',
            name='has_priority',
            field=models.BooleanField(default=False),
        ),
    ]