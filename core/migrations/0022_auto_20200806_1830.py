# Generated by Django 2.2.4 on 2020-08-06 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_variation_variationname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='variation',
            name='variationName',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
